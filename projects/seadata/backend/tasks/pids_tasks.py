import os

from b2stage.endpoints.commons import path
from restapi.connectors.celery import send_errors_by_email
from restapi.utilities.logs import log
from restapi.utilities.processes import start_timeout, stop_timeout
from seadata.tasks.seadata import celery_app, r

TIMEOUT = 180


def recursive_list_files(imain, irods_path):

    data = []
    for current in imain.list(irods_path):
        ifile = path.join(irods_path, current, return_str=True)
        if imain.is_dataobject(ifile):
            data.append(ifile)
        else:
            data.extend(recursive_list_files(imain, ifile))

    return data


@celery_app.task(bind=True)
@send_errors_by_email
def cache_batch_pids(self, irods_path):

    with celery_app.app.app_context():

        log.info("Task cache_batch_pids working on: {}", irods_path)

        try:
            with celery_app.get_service(service="irods") as imain:

                stats = {
                    "total": 0,
                    "skipped": 0,
                    "cached": 0,
                    "errors": 0,
                }

                try:
                    start_timeout(TIMEOUT)
                    data = recursive_list_files(imain, irods_path)
                    log.info("Found {} files", len(data))
                    stop_timeout()
                except BaseException as e:
                    log.error(e)

                # for current in imain.list(irods_path):
                #     ifile = path.join(irods_path, current, return_str=True)

                for ifile in data:

                    stats["total"] += 1

                    pid = r.get(ifile)
                    if pid is not None:
                        stats["skipped"] += 1
                        log.debug(
                            "{}: file {} already cached with PID: {}",
                            stats["total"],
                            ifile,
                            pid,
                        )
                        self.update_state(state="PROGRESS", meta=stats)
                        continue

                    try:
                        start_timeout(TIMEOUT)
                        metadata, _ = imain.get_metadata(ifile)
                        pid = metadata.get("PID")
                        stop_timeout()
                    except BaseException as e:
                        log.error(e)

                    if pid is None:
                        stats["errors"] += 1
                        log.warning(
                            "{}: file {} has not a PID assigned",
                            stats["total"],
                            ifile,
                            pid,
                        )
                        self.update_state(state="PROGRESS", meta=stats)
                        continue

                    r.set(pid, ifile)
                    r.set(ifile, pid)
                    log.verbose(
                        "{}: file {} cached with PID {}", stats["total"], ifile, pid
                    )
                    stats["cached"] += 1
                    self.update_state(state="PROGRESS", meta=stats)

                self.update_state(state="COMPLETED", meta=stats)
                log.info(stats)
                return stats
        except BaseException as e:
            log.error(e)
            log.error(type(e))


@celery_app.task(bind=True)
@send_errors_by_email
def inspect_pids_cache(self):

    with celery_app.app.app_context():

        log.info("Inspecting cache...")
        counter = 0
        cache = {}
        for key in r.scan_iter("*"):
            folder = os.path.dirname(r.get(key))

            prefix = str(key).split("/")[0]
            if prefix not in cache:
                cache[prefix] = {}

            if folder not in cache[prefix]:
                cache[prefix][folder] = 1
            else:
                cache[prefix][folder] += 1

            counter += 1
            if counter % 10000 == 0:
                log.info("{} pids inspected...", counter)

        for prefix in cache:
            for pid_path in cache[prefix]:
                log.info(
                    "{} pids with prefix {} from path: {}",
                    cache[prefix][pid_path],
                    prefix,
                    pid_path,
                )
        log.info("Total PIDs found: {}", counter)
