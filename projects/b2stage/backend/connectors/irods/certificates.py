"""
Using x509 certificates
"""

import os
import pwd
import re
from datetime import datetime, timedelta

import dateutil.parser
import pytz
from OpenSSL import crypto
from plumbum import local
from plumbum.commands.processes import ProcessExecutionError
from restapi.utilities.logs import log


# Mostly excluded from coverage because it is only used by a very specific service
# No further tests will be included in the core
class Certificates:

    _dir = os.getenv("CERTDIR")
    _proxyfile = "userproxy.crt"

    def __init__(self):
        log.warning(
            "All methods of this class are static, no need to create an instance"
        )

    @classmethod
    def get_dn_from_cert(cls, certdir, certfilename, ext="pem"):

        dn = ""
        cpath = os.path.join(cls._dir, certdir, f"{certfilename}.{ext}")
        with open(cpath) as fh:
            content = fh.read()
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, content)
            sub = cert.get_subject()

            for tup in sub.get_components():
                dn += f"/{tup[0].decode()}={tup[1].decode()}"

            log.debug("Host DN computed is {}", dn)
            return dn

    @staticmethod
    def generate_csr_and_key(user="TestUser"):
        """
        TestUser is the user proposed by the documentation,
        which will be ignored
        """
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 1024)
        req = crypto.X509Req()
        req.get_subject().CN = user
        req.set_pubkey(key)
        req.sign(key, "sha1")
        # print("CSR", key, req)
        return key, req

    @staticmethod
    def set_globus_proxy_cert(key, cert):  # , proxy=None):

        os.environ["X509_USER_KEY"] = key
        os.environ["X509_USER_CERT"] = cert

        # NOTE: for proxy we use above as temporary fix
        # check in the future why the right variable doesn't work anymore
        # os.environ['X509_USER_PROXY'] = proxy

    @classmethod
    def globus_proxy(
        cls,
        proxy_file=None,
        user_proxy=None,
        cert_dir=None,
        myproxy_host=None,
        cert_name=None,
        cert_pwd=None,
    ):

        if cert_dir is None:
            os.environ["X509_CERT_DIR"] = os.path.join(cls._dir, "simple_ca")
        else:
            os.environ["X509_CERT_DIR"] = cert_dir

        cpath = os.path.join(cls._dir, user_proxy)

        ################
        # 1. b2access
        if proxy_file is not None:
            log.debug("Certificate path: {}", proxy_file)
            Certificates.set_globus_proxy_cert(key=proxy_file, cert=proxy_file)

        ################
        # 2. normal certificates (e.g. 'guest')
        elif os.path.isdir(cpath):
            Certificates.set_globus_proxy_cert(
                key=os.path.join(cpath, "userkey.pem"),
                cert=os.path.join(cpath, "usercert.pem"),
            )

        ################
        # 3. mattia's certificates?
        elif myproxy_host is not None:

            proxy_cert_file = cpath + ".pem"
            if not os.path.isfile(proxy_cert_file):
                # Proxy file does not exist
                valid = False
            else:
                valid, not_before, not_after = Certificates.check_cert_validity(
                    proxy_cert_file
                )
                if not valid:
                    log.warning(
                        "Invalid proxy certificate for {}." + " Validity: {} - {}",
                        user_proxy,
                        not_before,
                        not_after,
                    )

            # Proxy file does not exist or expired
            if not valid:
                log.warning("Creating a new proxy for {}", user_proxy)
                try:

                    irods_env = os.environ

                    valid = Certificates.get_myproxy_certificate(
                        # FIXME: X509_CERT_DIR should be enough
                        irods_env=irods_env,
                        irods_user=user_proxy,
                        myproxy_cert_name=cert_name,
                        irods_cert_pwd=cert_pwd,
                        proxy_cert_file=proxy_cert_file,
                        myproxy_host=myproxy_host,
                    )

                    if valid:
                        log.info("Proxy refreshed for {}", user_proxy)
                    else:
                        log.error("Got invalid proxy: user {}", user_proxy)

                except Exception as e:
                    log.critical("Cannot refresh proxy: user {}", user_proxy)
                    log.critical(e)

            ##################
            if valid:
                Certificates.set_globus_proxy_cert(
                    key=proxy_cert_file, cert=proxy_cert_file
                )
            else:
                log.critical("Cannot find a valid certificate file")
                return False

            Certificates.check_x509_permissions()

        return True

    @staticmethod
    def path_is_readable(filepath):
        return (os.path.isfile(filepath) or os.path.isdir(filepath)) and os.access(
            filepath, os.R_OK
        )

    @staticmethod
    def check_x509_permissions():

        os_user = pwd.getpwuid(os.getuid()).pw_name
        failed = False

        # Check up with X509 variables
        for key, filepath in os.environ.items():

            # skip non certificates variables
            if not key.startswith("X509"):
                continue

            # check if current HTTP API user can read needed certificates
            if key.lower().endswith("cert_dir"):
                # here it has been proven to work even if not readable...
                if not Certificates.path_is_readable(filepath):
                    failed = True
                    log.error(
                        "{} variable ({}) not readable by {}", key, filepath, os_user
                    )
            else:
                os_owner = pwd.getpwuid(os.stat(filepath).st_uid).pw_name
                if os_user != os_owner:
                    failed = True
                    log.error(
                        "{} variable ({}) owned by {} instead of {}",
                        key,
                        filepath,
                        os_owner,
                        os_user,
                    )

        if failed:
            raise AttributeError("Certificates ownership problem")

    @staticmethod
    def check_cert_validity(certfile, validity_interval=1):
        args = ["x509", "-in", certfile, "-text"]

        # TODO: change the openssl bash command with the pyOpenSSL API
        # if so we may remove 'plumbum' from requirements of rapydo-http repo

        try:

            # Pattern in plumbum library for executing a shell command
            command = local["openssl"]
            log.debug("Executing command openssl {}", command, args)
            output = command(args)

        except ProcessExecutionError as e:
            raise e

        pattern = re.compile(
            r"Validity.*\n\s*Not Before: (.*)\n" + r"\s*Not After *: (.*)"
        )
        validity = pattern.search(output).groups()

        not_before = dateutil.parser.parse(validity[0])
        not_after = dateutil.parser.parse(validity[1])
        now = datetime.now(pytz.utc)
        valid = (not_before < now) and (
            not_after > now - timedelta(hours=validity_interval)
        )

        return valid, not_before, not_after

    @staticmethod
    def get_myproxy_certificate(
        irods_env,
        irods_user,
        myproxy_cert_name,
        irods_cert_pwd,
        proxy_cert_file,
        duration=168,
        myproxy_host="grid.hpc.cineca.it",
    ):
        try:
            myproxy = local["myproxy-logon"]
            if irods_env is not None:
                myproxy = myproxy.with_env(**irods_env)

            (
                myproxy[
                    "-s",
                    myproxy_host,
                    "-l",
                    irods_user,
                    "-k",
                    myproxy_cert_name,
                    "-t",
                    str(duration),
                    "-o",
                    proxy_cert_file,
                    "-S",
                ]
                << irods_cert_pwd
            )()

            return True
        except Exception as e:
            log.error(e)
            return False
