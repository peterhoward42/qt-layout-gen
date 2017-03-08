"""
This class is responsible for interpreting the word from the LHS of an InputTextRecord,
and instantiating (or finding) the QObject it is calling for.
"""

class _ParentMaker(object):

    @classmethod
    def make(cls, record):
        """
        Entry point for the parent-making operation. When successful, it returns the
        QObject and the parent name that has been extracted from the record.
        Otherwise it returns a non-None BuildError.s
        :param record: The InputTextRecord to make the QObject parent for.
        :return: A 3-tuple: (QObject, parent_name, BuildError)
        """
        q_obj = None
        name = None
        err = None

        if cls._has_two_colons(record):
            q_obj, name, err = cls._find_existing_qobject(record)
        elif cls._starts_with_q(record):
            q_obj, name, err = cls._make_qtype(record)
        elif cls._starts_with_keyword(lhs_word):
            q_obj, name, err = cls._make_keyword_type(record)

        # If any of these reported an error - give up
        if err:
            return None, None, err

        # If none of these fired - give up
        if q_obj is None:
            first_word = record.words[0]
            return None, None, BuildError(
                ('The first word: <%s> of your record defined here: <%s>, does not ' + \
                'conform to any of the legal forms') % (first_word, record.file_location))

        # We succeeded
        return q_obj, name, None