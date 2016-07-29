class Fort(object):

    def __init__(self, data):
        self.fort_id = data.get("id", "")
        self.latitude = data.get("latitude", 0.0)
        self.longitude = data.get("longitude", 0.0)
        self.enabled = data.get("enabled", 1)
        self.last_modified_timestamp_ms = data.get("last_modified_timestamp_ms", 0)
        self.fort_type = data.get("type", 0)

class PokeStop(Fort):

    def __init__(self, data):
        super(PokeStop, self).__init__(data)
        self.active_fort_modifier = data.get("active_fort_modifier", "")

        lure_info = data.get("lure_info", {})
        self.lure_expires_timestamp_ms = lure_info.get("lure_expires_timestamp_ms", 0)
        self.lure_encounter_id = lure_info.get("encounter_id", 0)
        self.lure_encounter_id = lure_info.get("active_pokemon_id", 0)
        self.fort_type = 1

        """
               "id":"7ae7f45fb3e643d7a846b2d3f60e27e7.16",
               "lure_info":{  
                  "active_pokemon_id":129,
                  "fort_id":"7ae7f45fb3e643d7a846b2d3f60e27e7.16",
                  "lure_expires_timestamp_ms":1469759077519,
                  "encounter_id":2028465687
               },
               "last_modified_timestamp_ms":1469758177570,
               "latitude":40.781831,
               "active_fort_modifier":"9QM=",
               "longitude":-73.97412,
               "enabled":1,
               "type":1
        """

class Gym(Fort):

    def __init__(self, data):
        super(Gym, self).__init__(data)

        self.is_in_battle = data.get("is_in_battle", 0)
        self.is_in_battle = True if self.is_in_battle == 1 else False

        self.guard_pokemon_id = data.get("guard_pokemon_id", 0)
        self.owned_by_team = data.get("owned_by_team", 0)
        self.gym_points = data.get("gym_points", 0)

        """
               "last_modified_timestamp_ms":1469759071295,
               "guard_pokemon_id":6,
               "latitude":40.781115,
               "gym_points":2250,
               "id":"5470838db6d54ed4aa235bd2c0fe744e.16",
               "owned_by_team":3,
               "longitude":-73.973744,
               "enabled":1,
               "is_in_battle":1
        """

class Cell(object):

    def __init__(self, data):
        self.spawn_points = []
        self.gyms = []
        self.pokestops = []

        self.cell_id = data.get("s2_cell_id", 0)

        spawn_points = data.get("spawn_points", [])
        for spawn in spawn_points:
            self.spawn_points.append((spawn["latitude"], spawn["longitude"]))

        forts = data.get("forts", [])
        for fort in forts:
            if fort.get("type", 2) == 1:
                self.pokestops.append(PokeStop(fort))
            else:
                self.gyms.append(Gym(fort))

class WorldMap(object):

    def __init__(self):
        self.cells = {}

    def update_map_objects(self, data):
        self.data = data
        """
        # Patch this up later
        cells = data.get("cells", [])
        for cell_data in cells:
            cell = Cell(cell_data)
            self.cells[cell.cell_id] = cell
        """
