"""
This module defines the _RecordLookup class.
"""

from builderror import BuildError


class _RecordLookup(object):
    """
    Provides a look up service for InputTextRecords by parent name.
    """

    def __init__(self):
        self.records = {}

    def _populate(self, input_text_records):
        """
        Populates the look up table, protecting against duplicate definitions.
        :param input_text_records: The input text records to build from.
        :return: BuildError or None
        """
        for record in input_text_records:
            name = record.parent_name
            # Object to duplicates
            if name in self.records:
                existing_file_location = self.records[name].file_location
                conflicting_file_location = record.file_location
                return BuildError(
                    ('You cannot use the parent name: <%s>, which is specified ' + \
                    'here: <%s>, because you already used it here: <%s>') %
                    (name, conflicting_file_location, existing_file_location))
            # Register the record in the dictionary
            self.records[name] = record
