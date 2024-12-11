from controllers.graph import setup_callbacks as graph_callbacks
from controllers.mechanism import setup_callbacks as mechanism_callbacks
from controllers.noise import setup_callbacks as noise_callbacks
from controllers.lock_data import setup_callbacks as lock_data_callbacks
from controllers.data_summary import setup_callbacks as data_summary_callbacks



def setup_callbacks():
    graph_callbacks()
    noise_callbacks()
    mechanism_callbacks()
    lock_data_callbacks()
    data_summary_callbacks()
