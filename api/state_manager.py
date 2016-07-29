from .player import Player
from .inventory import Inventory
from .worldmap import WorldMap 

class StateManager(object): 

    def __init__(self):

        self.response_map = {
            "GET_PLAYER": self._parse_player,
            "GET_INVENTORY": self._parse_inventory,
            "GET_MAP_OBJECTS": self._parse_map,
            "ENCOUNTER": self._parse_encounter,
        }

        self.method_returns_states = {
            "GET_PLAYER": ["player"],
            "GET_INVENTORY": ["player", "inventory", "pokemon", "pokedex"],
            "CHECK_AWARDED_BADGES": [],
            "DOWNLOAD_SETTINGS": [],
            "GET_HATCHED_EGGS": [],
            "GET_MAP_OBJECTS": ["worldmap"],
            "ENCOUNTER": ["encounter"],
        }

        self.method_mutates_states = {
            "GET_PLAYER": [],
            "GET_INVENTORY": [],
            "CHECK_AWARDED_BADGES": [],
            "DOWNLOAD_SETTINGS": [],
            "GET_HATCHED_EGGS": [],
            "GET_MAP_OBJECTS": ["worldmap"],
            "ENCOUNTER": ["encounter"]
        }

        self.current_state = {}

        self.staleness = {}

    def is_stale(self, key):
        return self.staleness.get(key, True)

    def is_state_cached(self, method):
        affected_states = self.method_returns_states[method]
        for state in affected_states:
            if self.is_stale(state):
                return False
        return True

    def filter_cached_methods(self, method_keys):
        will_be_stale = {}
        uncached_methods = []
        for method in method_keys:
            affected_states = self.method_mutates_states[method]
            if len(affected_states) > 0:
                uncached_methods.append(method)
                for state in affected_states:
                    will_be_stale[state] = True
            else:
                returned_states = self.method_returns_states[method]
                for state in returned_states:
                    if self.is_stale(state) or will_be_stale.get(state, False):
                        uncached_methods.append(method)
                        break
            if method not in uncached_methods:
                print("Method " + method + " is cached, using cached data")
        return uncached_methods
            

    def _update_state(self, data):
        for key in data:
            value = data.get(key, None)
            if value is None:
                continue
            self.current_state[key] = data[key]
            self.staleness[key] = False

    def get_state(self):
        return self.current_state

    def get_state_filtered(self, keys):
        return_object = {}
        for key in keys:
            return_object[key] = self.current_state.get(key, None)
        return self.current_state

    def mark_stale(self, methods):
        for method in methods:
            #for state in self.method_mutates_states.get(method, []):
            for state in self.method_mutates_states[method]:
                self.staleness[method] = True

    def update_with_response(self, key, response):
        print("Mutating state for " + key)
        if key not in self.response_map:
            print(response)
            print("Unimplemented response " + key)
        self.response_map[key](response)

    def _parse_player(self, response):
        current_player = self.current_state.get("player", None)
        if current_player is None:
            current_player = Player()
        current_player.update_get_player(response)
        self._update_state({"player": current_player})

    def _parse_inventory(self, response):
        new_inventory = Inventory(response)

        new_state = {}

        new_state["inventory"] = new_inventory.items
        new_state["pokedex"] = new_inventory.pokedex_entries
        new_state["candy"] = new_inventory.candy
        new_state["pokemon"] = new_inventory.pokemon
        new_state["eggs"] = new_inventory.eggs

        current_player = self.current_state.get("player", None)
        if current_player is None:
            current_player = Player()
        current_player.update_get_inventory_stats(response)
        new_state["player"] = current_player

        self._update_state(new_state)

    def _parse_map(self, response):
        current_map = self.current_state.get("worldmap", None)
        if current_map is None:
            current_map = WorldMap()
        current_map.update_map_objects(response)

        self._update_state({"worldmap": current_map})

    def _parse_encounter(self, response):
        self._update_state({"encounter": {"status": response.get("status", 0)}})
