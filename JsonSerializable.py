class JsonSerializable:
    # Return a JSON serializable object (list, dict, string, number)
    def __json__(self):
        raise "Implement __json__()"
