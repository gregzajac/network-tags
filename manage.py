#!/usr/bin/env python3

import json
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import click
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

logging.basicConfig(
    format="[%(levelname)s] %(name)s: %(message)s\n", level=logging.INFO
)
manage_logger = logging.getLogger("manage.py")


BASE_DIR = Path(__file__).resolve().parent
APPLICATION_CONFIG_PATH = BASE_DIR / "config"
DOCKER_PATH = BASE_DIR / "docker"
RUNNING_INFO = "Running with {} settings"


def set_env(variable: str, default: str) -> None:
    """
    For given variable, replace its value with the one existing in env variables
    Otherwise set the new default value
    """
    os.environ[variable] = os.environ.get(variable, default)


# Ensure to have always set the app configuration
set_env("APPLICATION_CONFIG", "development")


def get_app_config_file(config: str) -> Path:
    """Get path to given config file name"""
    return APPLICATION_CONFIG_PATH / f"{config}.json"


def get_docker_compose_file(config: str) -> Path:
    """Get path to aprioriate docker compose file"""
    return DOCKER_PATH / f"{config}.yml"


def set_app_config(config: str) -> None:
    """Sets the application config vars based on JSON config file"""

    try:
        config_file = get_app_config_file(config)
        with open(config_file) as f:
            config = json.load(f)

        config = dict((i["name"], i["value"]) for i in config)

        for key, value in config.items():
            set_env(key, value)

    except FileNotFoundError:
        manage_logger.error(f"Config file not found in {config_file}")
        sys.exit(1)


@click.group()
def cli():
    pass


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("subcommand", nargs=-1, type=click.Path())
def flask(subcommand: str) -> None:
    """Flask commands related to application"""

    set_app_config(os.environ.get("APPLICATION_CONFIG"))
    manage_logger.info(RUNNING_INFO.format(os.environ.get("APPLICATION_CONFIG")))

    cmdline = ["flask"] + list(subcommand)

    try:
        p = subprocess.Popen(cmdline)
        p.wait()
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        p.wait()


def create_docker_compose_cmdline(args: str = None) -> list:
    """
    Create docker-compose command with aprioriate config and docker file
    It uses prefix `sudo -E` for managing docker-compose as a root with
    inherited environment vars
    """

    config = os.environ.get("APPLICATION_CONFIG")
    docker_compose_file = get_docker_compose_file(config)

    if not docker_compose_file.exists():
        raise ValueError(f"Docker compose file {docker_compose_file} not found")

    command_line = [
        "sudo",
        "-E",
        "docker-compose",
        "-p",
        config,
        "-f",
        docker_compose_file,
    ]

    if args:
        command_line.extend(args.split(" "))

    return command_line


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("subcommand", nargs=-1, type=click.Path())
def compose(subcommand: str) -> None:
    """Wrapper on `sudo -E docker-compose` command"""

    set_app_config(os.environ.get("APPLICATION_CONFIG"))
    manage_logger.info(RUNNING_INFO.format(os.environ.get("APPLICATION_CONFIG")))

    cmdline = create_docker_compose_cmdline() + list(subcommand)

    try:
        p = subprocess.Popen(cmdline)
        p.wait()
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        p.wait()


def run_sql(statements: list) -> None:
    """Run given sql statements list in POSTGRES_DB database"""

    try:
        conn = psycopg2.connect(
            dbname=os.environ.get("POSTGRES_DB"),
            user=os.environ.get("POSTGRES_USER"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            host=os.environ.get("POSTGRES_HOSTNAME"),
            port=os.environ.get("POSTGRES_PORT"),
        )

        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        for statement in statements:
            cursor.execute(statement)

        cursor.close()
        conn.commit()

    except Exception:
        manage_logger.error("Unexpected error", exc_info=True)


def wait_for_logs(cmdline: list, message: str) -> None:
    """
    Wait for given message in executed command logs
    Helper for testing, waiting for ready database connection
    before executing sql statements
    """
    manage_logger.info("starting wait for logs...")
    logs = subprocess.check_output(cmdline)
    while message not in logs.decode("utf-8"):
        time.sleep(0.1)
        logs = subprocess.check_output(cmdline)


@cli.command()
def create_db() -> None:
    """Create initial database if not exists"""

    set_app_config(os.environ.get("APPLICATION_CONFIG"))
    manage_logger.info(RUNNING_INFO.format(os.environ.get("APPLICATION_CONFIG")))

    try:
        run_sql([f"CREATE DATABASE {os.environ.get('APPLICATION_DB')};"])
        manage_logger.info(
            f"Database {os.environ.get('APPLICATION_DB')} has been created"
        )

    except psycopg2.errors.DuplicateDatabase:
        print(f"The database {os.environ.get('APPLICATION_DB')} already exists")
    except Exception:
        manage_logger.error("Database has not been created!", exc_info=True)
        sys.exit(1)


@cli.command()
@click.argument("filenames", nargs=-1)
def test(filenames: str) -> None:
    """Running tests in contenerized testing environment"""
    # Runs docker-compose with postgresql, creates database and
    # executes pytest command on local application with
    # testing config
    # After finishing tests docker container with postgres downs

    os.environ["APPLICATION_CONFIG"] = "testing"
    set_app_config(os.environ.get("APPLICATION_CONFIG"))
    manage_logger.info(RUNNING_INFO.format(os.environ.get("APPLICATION_CONFIG")))

    cmdline = create_docker_compose_cmdline("up -d")
    subprocess.call(cmdline)

    cmdline = create_docker_compose_cmdline("logs db")
    wait_for_logs(cmdline, "ready to accept connections")
    time.sleep(0.5)

    run_sql([f"CREATE DATABASE {os.environ.get('APPLICATION_DB')}"])

    cmdline = ["pytest", "-svv", "--cov=application"]
    cmdline.extend(filenames)

    subprocess.call(cmdline)

    cmdline = create_docker_compose_cmdline("down")
    subprocess.call(cmdline)


@cli.command()
def run_dev():
    """TODO: Running app with initialised db and added sample data"""
    # Wrapper for starting app in development settings with database
    # and added sample data on it (below example for development):
    # - run docker-compose up -d
    # - run create_db
    # - run flask db init
    # - run flask db migrate
    # - run flask db upgrade
    # - run flask db-manage add-data
    pass


if __name__ == "__main__":
    cli()
