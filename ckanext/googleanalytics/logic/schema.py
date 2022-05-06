from ckan.logic.schema import validator_args


@validator_args
def googleanalytics_package_stats_show(not_empty):
    return {"id": [not_empty]}


@validator_args
def googleanalytics_resource_stats_show(not_empty):
    return {"id": [not_empty]}
