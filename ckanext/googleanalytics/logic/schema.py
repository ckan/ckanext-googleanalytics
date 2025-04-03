from ckan.logic.schema import validator_args


@validator_args
def package_stats_show(not_empty):
    return {"id": [not_empty]}


@validator_args
def resource_stats_show(not_empty):
    return {"id": [not_empty]}


@validator_args
def event_report(
    not_empty, isodate, json_list_or_string, default, ignore_empty
):
    return {
        "start_date": [not_empty, isodate],
        "end_date": [not_empty, isodate],
        "name": [ignore_empty],
        "metrics": [ignore_empty],
        "dimensions": [ignore_empty],
    }
