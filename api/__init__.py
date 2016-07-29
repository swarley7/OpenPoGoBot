from pgoapi import PGoApi
from pgoapi.auth_ptc import AuthPtc
from pgoapi.auth_google import AuthGoogle
import time
import json
from .state_manager import StateManager

class PoGoApi(object):

    def __init__(self, provider="google", username="", password=""):
        self._api = PGoApi()

        self.provider = provider
        self.username = username
        self.password = password

        self.current_position = (0,0,0)

        self.state = StateManager()

        self._pending_calls = {}
        self._pending_calls_keys = []

    def login(self):
        provider, username, password = self.provider, self.username, self.password
        return self._api.login(provider, username, password)

        # TODO: Figure out why the below doesn't work
        """
        if provider == 'ptc':
            self._api._auth_provider = AuthPtc()
        elif provider == 'google':
            self._api._auth_provider = AuthGoogle()

        if not self._api._auth_provider.login(username, password):
            print("Failed")
            return False

        # making a standard call, like it is also done by the client
        self.get_player()
        self.get_hatched_eggs()
        self.get_inventory()
        self.check_awarded_badges()
        self.download_settings(hash="05daf51635c82611d1aac95c0b051d3ec088a930")

        response = self.call(ignore_expiration=True, ignore_cache=True)
        print(response)

        if response is None:
            return False

        if 'api_url' in response:
            self._api._api_endpoint = ('https://{}/rpc'.format(response['api_url']))
            print("setting api_url")
        else:
            print("unexpected response")
            return False

        if 'auth_ticket' in response:
            self._auth_provider.set_ticket(response['auth_ticket'].values())
            print("setting auth ticket")

        return True
        """

    def set_position(self, lat, lng, alt):
        self._api.set_position(lat, lng, alt)

    def get_position(self):
        return self._api.get_position()

    def get_rpc_methods(self):
        return self._api.list_curr_methods()

    def __getattr__(self, func):
        def function(*args, **kwargs):
            func_name = str(func).upper()
            print("[API] Queueing " + func_name)
            self._pending_calls[func_name] = (args, kwargs)
            self._pending_calls_keys.append(func_name)
            return self

        return function

    def get_expiration_time(self):
        ticket = self._api._auth_provider.get_ticket()
        if ticket is False:
            return 0
        for field in ticket:
            if isinstance(field, int):
                return int(field/1000 - time.time())
        return 0

    def call(self, ignore_expiration=False, ignore_cache=False):
        methods, method_keys, self._pending_calls, self._pending_calls_keys = self._pending_calls, self._pending_calls_keys, {}, []
        if self.get_expiration_time() < 60 and ignore_expiration is False:
            print("[API] Token has expired, attempting to log back in...")
            while self.login() is False:
                print("[API] Failed to login. Waiting 15 seconds...")
                time.sleep(15)

        uncached_method_keys = self.state.filter_cached_methods(method_keys) if ignore_cache is False else method_keys
        if len(uncached_method_keys) == 0:
            return self.state.get_state()

        for _ in range(3):
            for method in uncached_method_keys:
                my_args, my_kwargs = methods[method]
                getattr(self._api, method)(*my_args, **my_kwargs)

            results = self._api.call()
            if results is False or results is None or results.get('status_code', 0) != 1:
                print("[API] API call failed. Retrying in 5 seconds...")
                time.sleep(5)
            else:
                with open('api-test.txt', 'w') as f:
                    f.write(str(results))
                #print(results)
                #return results

                self.state.mark_stale(methods)

                responses = results.get("responses", {})
                for key in responses:
                    self.state.update_with_response(key, responses[key])
                return self.state.get_state()
        return None

