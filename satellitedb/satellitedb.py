# MIT License
# Copyright (c) 2021 Data Dlog

"""
Purpose

The database object schemas are generated by the main module. 
"""

import logging
import os
from datetime import datetime

import yaml
from schema_generator import schema_generator

# datetime object containing current date and time
now = datetime.now()

# Get the current execute file path
file_path = os.path.realpath(__file__)

# Get the current directory
cur_dir = os.path.dirname(file_path)

# Logs directory
log_dir = os.path.join(cur_dir, "logs")

log_f = "satellitedb-log-" + now.strftime("%Y%m%d%H%M%S" + ".txt")
log_fname = os.path.join(log_dir, log_f)

logging.basicConfig(
    filename=log_fname,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
)


logger = logging.getLogger(__name__)

# Configuration files
app_cfg_file = os.path.join(cur_dir, "config", "app.yml")
db_cfg_file = os.path.join(cur_dir, "config", "db.yml")


def load_cfg(cfg_file):
    """The configuration files are loaded using this function.
    Args:
        param cfg_file: Configuration file
    Returns:
        value: The return value.
    Raises:
        FileNotFoundError: File not found error, if there is no config file exists
    """
    cfg = None

    try:
        with open(cfg_file, "r") as file:
            cfg = yaml.safe_load(file)
        return cfg
    except FileNotFoundError:
        logger.error("Config file not found - {}".format(cfg_file))
        raise


def create_db_url(db_type, host, db, schma, port, db_usr, db_pass):
    """Creates database URL to connect database.
    Args:
        param db_type: Database type like PostgreSQL, MySQL, etc..
        param host: Database host name or instance name
        param db: Database name
        param schma: Database schema name
        param port: Database port
        param db_usr: Database username
        param db_pass: Database password
    Returns:
        value: The return value, database URL.
        example:
          # postgresql://usr_dummy:pass_dummy@host_dummy:1234/db_dummy?schma_dummy
    Raises:
        TypeError: If any of the DB parameter value is empty

    """
    try:
        if db_type == "postgresql":
            db_uri = (
                "postgresql://"
                + str(db_usr)
                + ":"
                + str(db_pass)
                + "@"
                + str(host)
                + ":"
                + str(port)
                + "/"
                + str(db)
                + "?"
                + schma
            )
        return db_uri
    except TypeError:
        logger.error("One of the DB parameter is empty")
        raise


if __name__ == "__main__":

    logger.info("Loading app config from file - {}".format(app_cfg_file))
    app_cfg = load_cfg(app_cfg_file)
    logger.info("Loading database config from file - {}".format(db_cfg_file))
    db_cfg = load_cfg(db_cfg_file)

    host = None
    port = None
    db = None
    schma = None
    db_usr = None
    db_pass = None

    db_type = None
    incl_db_objs = None
    gh_url = None
    gh_tkn = None
    tar_loc = None
    file_extn = None

    if app_cfg is not None:
        try:
            db_type = app_cfg["db_config"]["db_type"]
            incl_db_objs = app_cfg["db_config"]["db_objects"]
            gh_url = app_cfg["github_config"]["remote_url"]
            gh_tkn = app_cfg["github_config"]["access_token"]
            tar_loc = app_cfg["output"]["schema_dump_loc"]
            file_extn = app_cfg["output"]["file_format"]
        except KeyError as error:
            logger.error("Key not found - {}".format(error))
            raise

    else:
        msg = "App config is empty"
        logger.error(msg)
        raise Exception(msg)

    if db_cfg is not None:
        try:
            if db_type != "sqlite":
                host = db_cfg[db_type]["host_name"]
                port = db_cfg[db_type]["port"]
                db = db_cfg[db_type]["database_name"]
                schma = db_cfg[db_type]["schema_name"]
                db_usr = db_cfg[db_type]["user_name"]
                db_pass = db_cfg[db_type]["password"]
        except KeyError as error:
            logger.error("Key not found - {}".format(error))
            raise

    else:
        msg = "DB config is empty"
        logger.error(msg)
        raise Exception(msg)

    logger.info("Creating DB URL")
    db_url = None

    if db_type == "sqlite":
        db_url = db_cfg[db_type]["db_url"]
    else:
        db_url = create_db_url(db_type, host, db, schma, port, db_usr, db_pass)

    if len(db_url) > 1:
        schema_generator.main(db_type, db_url, tar_loc, file_extn, incl_db_objs)
    else:
        msg = "DB url is empty"
        logger.error(msg)
        raise Exception(msg)
