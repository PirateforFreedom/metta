from omegaconf import OmegaConf
import pufferlib
import pufferlib.utils
import pufferlib.vector
import hydra


def make_env_func(cfg: OmegaConf, render_mode='rgb_array'):
    env = hydra.utils.instantiate(cfg, render_mode=render_mode)
    env.emulated = None
    env.single_observation_space = env.observation_space
    env.single_action_space = env.action_space
    env.num_agents = env.player_count

    return env

def make_vecenv(cfg: OmegaConf, num_envs=1, batch_size=None, num_workers=1, render_mode=None, **kwargs):
    vec = cfg.vectorization
    if vec == 'serial' or num_workers == 1:
        vec = pufferlib.vector.Serial
    elif vec == 'multiprocessing':
        vec = pufferlib.vector.Multiprocessing
    elif vec == 'ray':
        vec = pufferlib.vector.Ray
    else:
        raise ValueError('Invalid --vector (serial/multiprocessing/ray).')

    vecenv_args = dict(
        env_kwargs=dict(cfg = dict(**cfg.env), render_mode=render_mode),
        num_envs=num_envs,
        num_workers=num_workers,
        batch_size=batch_size or num_envs,
        backend=vec,
        **kwargs
    )

    vecenv = pufferlib.vector.make(make_env_func, **vecenv_args)
    return vecenv
