from firebase import firebase


# Class used in order to instantiate and initiate the connection to the firebase database
class FirebaseDAO:
    def __init__(self):
        self.firebase = firebase.FirebaseApplication('https://irishmusicartists.firebaseio.com/', None)

    # 1.
    # returns all the values from the table
    def get_all(self, table):
        return self.firebase.get('/{0}'.format(table), None)

    # def get_id_from_table_value(self, table, object_id):
    #     all_value = self.get_all(table)
    #     for current in all_value:
    #         if all_value.get(current)['id'] == int(object_id):
    #             return all_value.get(current)
    #     return None

    # 2.
    # gets all the values from a particular table and returns the ones having property_obj == value
    # this is used in order to get users with their email
    def get_object_by_property(self, table, property_obj, value):
        all_values = self.get_all(table)
        for val in all_values:
            if val:
                if val.get(property_obj) == value:
                    return val
        return None

    # 3.
    # returns a specific entity from its id
    def get_id_from_table(self, table, object_id):
        return self.firebase.get('/{0}'.format(table), object_id)

    # not used anymore as was generating a random id that was hard to deal with
    def add_to_table(self, table, obj):
        resp = self.firebase.post('/{0}'.format(table), obj)
        return resp

    # 4.
    # Counts all the entries in a particular table
    def get_table_count(self, table):
        all_value = self.firebase.get('/{0}'.format(table), None)
        if all_value:
            return len(all_value)
        else:
            return 0

    # 5.
    # add an entry to a specific place, allows to either create a new entry and update it in the future
    # https://stackoverflow.com/questions/37148414/updating-a-single-value-in-firebase-with-python
    def update(self, table, key, value):
        resp = self.firebase.put('/{0}'.format(table), key, value)
        return resp
