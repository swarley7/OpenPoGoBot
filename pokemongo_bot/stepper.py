# -*- coding: utf-8 -*-

from math import ceil
import json

from s2sphere import CellId, LatLng
from pgoapi.utilities import f2i
from pokemongo_bot.human_behaviour import sleep, random_lat_long_delta
from pokemongo_bot.utils import distance, format_time, convert_to_utf8
import pokemongo_bot.logger as logger


class Stepper(object):

    AVERAGE_STRIDE_LENGTH_IN_METRES = 0.60

    def __init__(self, bot):
        self.bot = bot
        self.api = bot.api
        self.config = bot.config

        self.pos = 1
        self.first_step = True
        self.step_limit = self.config.max_steps
        self.step_limit_squared = self.step_limit ** 2
        self.origin_lat = self.bot.position[0]
        self.origin_lon = self.bot.position[1]

    def take_step(self):
        position = (0, 0, 0)
        if self.first_step:
            self.first_step = False
            position = (self.origin_lat, self.origin_lon, 0.0)
        else:
            position_lat, position_lng, _ = self.api.get_position()
            position = (position_lat, position_lng, 0.0)

        self.api.set_position(*position)
        self._work_at_position(position[0], position[1], True)
        sleep(5)

    def walk_to(self, speed, lat, lng, alt):
        position_lat, position_lng, _ = self.api.get_position()
        dist = distance(position_lat, position_lng, lat, lng)
        steps = (dist / (self.AVERAGE_STRIDE_LENGTH_IN_METRES * speed))

        logger.log("[#] Walking from " + str((position_lat, position_lng)) + " to " + str((lat, lng)) + " for approx. " + str(format_time(ceil(steps))))
        if steps != 0:
            d_lat = (lat - position_lat) / steps
            d_long = (lng - position_lng) / steps

            for _ in range(int(steps)):
                position_lat, position_lng, _ = self.api.get_position()
                c_lat = position_lat + d_lat + random_lat_long_delta()
                c_long = position_lng + d_long + random_lat_long_delta()
                self.api.set_position(c_lat, c_long, alt)

                self.bot.heartbeat()
                sleep(1)  # sleep one second plus a random delta

                position_lat, position_lng, _ = self.api.get_position()
                self._work_at_position(position_lat, position_lng, False)

            self.bot.heartbeat()
            logger.log("[#] Finished walking")

    def _get_cell_id_from_latlong(self, radius=10):
        position_lat, position_lng, _ = self.api.get_position()
        origin = CellId.from_lat_lng(LatLng.from_degrees(position_lat, position_lng)).parent(15)
        walk = [origin.id()]

        # 10 before and 10 after
        next_cell = origin.next()
        prev_cell = origin.prev()
        for _ in range(radius):
            walk.append(prev_cell.id())
            walk.append(next_cell.id())
            next_cell = next_cell.next()
            prev_cell = prev_cell.prev()
        return sorted(walk)

    def _work_at_position(self, lat, lng, pokemon_only=False):
        cell_id = self._get_cell_id_from_latlong()
        timestamp = [0, ] * len(cell_id)
        self.api.get_map_objects(latitude=f2i(lat),
                                 longitude=f2i(lng),
                                 since_timestamp_ms=timestamp,
                                 cell_id=cell_id)

        response_dict = self.api.call()
        if response_dict is None:
            return
        # Passing data through last-location and location
        map_objects = response_dict["worldmap"].data
        if map_objects is not None:
            with open("web/location-{}.json".format(self.config.username), "w") as outfile:
                json.dump({"lat": lat, "lng": lng, "cells": convert_to_utf8(map_objects.get("map_cells"))}, outfile)
            with open("data/last-location-{}.json".format(self.config.username), "w") as outfile:
                outfile.truncate()
                json.dump({"lat": lat, "lng": lng}, outfile)
            if "status" in map_objects:
                if map_objects.get("status") is 1:
                    map_cells = map_objects.get("map_cells")
                # Sort all by distance from current pos - eventually this should build graph and A* it
                map_cells.sort(key=lambda x: distance(lat, lng, x["forts"][0]["latitude"], x["forts"][0]["longitude"]) if "forts" in x and x["forts"] != [] else 1e6)
                for cell in map_cells:
                    self.bot.work_on_cell(cell, pokemon_only)
