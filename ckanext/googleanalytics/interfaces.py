from ckan.plugins import Interface


class IGoogleAnalytics(Interface):
    def googleanalytics_skip_event(self, data):
        """Decide if sending data to GA must be skipped.
        """
        return False
