class Egg(object):
    """
     'captured_cell_id':1234567890,
     'is_egg':True,
     'id':1234567890,
     'egg_km_walked_target':5.0,
     'creation_time_ms':1234567890
    """

    def __init__(self, data):
        self.id = data.get("id", 0)
        self.walked_distance = data.get("egg_km_walked_start", 0.0)
        self.total_distance = data.get("egg_km_walked_target", 0.0)

        # Currently don't care about captured_cell_id, creation_time_ms

class Pokemon(object):

    """
     'move_2':26,
     'individual_defense':4,
     'stamina_max':18,
     'pokeball':1,
     'pokemon_id':27,
     'creation_time_ms':1234567890,
     'individual_attack':4,
     'move_1':216,
     'captured_cell_id':1234567890,
     'id':1234567890,
     'cp':30,
     'cp_multiplier':0.1234567890,
     'stamina':18,
     'height_m':0.1234567890,
     'weight_kg':1.23456790,
     'individual_stamina':14
    """

    def __init__(self, data):
        self.id = data.get("id", 0)
        self.pokemon_id = data.get("pokemon_id", 0)
        self.hp = data.get("individual_stamina", 0)
        self.max_hp = data.get("stamina_max", 0)
        self.combat_power = data.get("cp", 0)
        self.combat_power_multiplier = data.get("cp_multiplier", 0)
        self.attack = data.get("individual_attack", 0)
        self.defense = data.get("individual_defense", 0)
        self.stamina = data.get("individual_stamina", 0)

        # We don't care about the following at the moment
        # Pokeball, move_1, move_2, captured_cell_id, height_m, weight_kg, creation_time_ms
