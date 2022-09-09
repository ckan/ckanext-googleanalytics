from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from ckanext.googleanalytics import utils, config


def init_service(credentials_file):
    """Get a service that communicates to a Google API."""
    scope = ["https://www.googleapis.com/auth/analytics.readonly"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credentials_file, scopes=scope
    )

    return build("analytics", "v3", credentials=credentials)


def get_profile_id(service):
    """Get static profile ID or fetch one from the service.

    Get the profile ID for this user and the service specified by the
    'googleanalytics.id' configuration option. This function iterates
    over all of the accounts available to the user who invoked the
    service to find one where the account name matches (in case the
    user has several).

    If not user configured, the first account is used
    """

    profile_id = config.profile_id()
    if profile_id:
        return profile_id

    accounts = service.management().accounts().list().execute()

    if not accounts.get("items"):
        return None
    accountName = config.account()
    webPropertyId = config.tracking_id()
    for acc in accounts.get("items"):
        if not accountName or acc.get("name") == accountName:
            accountId = acc.get("id")

            profiles = (
                service.management()
                .profiles()
                .list(accountId=accountId, webPropertyId=webPropertyId)
                .execute()
            )

            if profiles.get("items"):
                return profiles.get("items")[0].get("id")

    return None
