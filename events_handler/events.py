from enum import Enum


class EventTypes(Enum):
    TSP_DATA_REQUEST = "tsp_data_requested"
    SOLVE = "solve"
    TSP_FILE_OPENED = "tsp_file_opened"
    PLOT_REQUEST = "plot_request"


class SubscriberRole(Enum):
    SUNSCRIBER = "subscriber"
    LISTENER = "listener"
    PROVIDER = "provider"
    CONSUMER = "consumer"


class EventsHandler:
    _subscribers = {}

    @classmethod
    def subscribe(cls, event_type: EventTypes, subscriber_role: SubscriberRole, fn):
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        if (subscriber_role, fn) not in cls._subscribers[event_type]:
            cls._subscribers[event_type].append((subscriber_role, fn))

    @classmethod
    def post_event(cls, event_type: EventTypes, data):
        if event_type not in cls._subscribers:
            return
        for role, fn in cls._subscribers[event_type]:
            if role == SubscriberRole.LISTENER:
                fn(data)
            if role == SubscriberRole.CONSUMER:
                for key, value in cls._subscribers.items():
                    print(value, type(value))
                provider = [value[0] for key, value in cls._subscribers.items() if value[0][0] == SubscriberRole.PROVIDER][0]
                print(provider)
                result = provider[1](data)
                return fn(result)

    @classmethod
    def dispatch_data(cls, event_type: EventTypes, data):
        if event_type not in cls._subscribers:
            return
        for role, fn in cls._subscribers[event_type]:
            return fn(data)
