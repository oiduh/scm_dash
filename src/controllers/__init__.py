from controllers.graph import setup_callbacks as graph_callbacks
from controllers.mechanism import setup_callbacks as mechanism_callbacks
from controllers.noise import setup_callbacks as noise_callbacks
from controllers.data_generation_summary import setup_callbacks as data_generation_summary_callbacks


def setup_callbacks():
    graph_callbacks()
    noise_callbacks()
    mechanism_callbacks()
    data_generation_summary_callbacks()
