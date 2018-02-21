#!/usr/bin/env python
import argparse
import logging
import os
import tensorflow as tf
import gym
from baselines import logger
from baselines.common import set_global_seeds
from baselines import bench
from baselines.a2c.a2c_cont import learn
from baselines.a2c.policies import GaussianMlpPolicy, RelaxedGaussianMlpPolicy

def train(env_id, num_timesteps, seed, logdir, relax, p_lr, vf_lr, cv_lr, cv_num, endwhendone, score, var_check, l2):
    env=gym.make(env_id)
    if logger.get_dir():
        env = bench.Monitor(env, os.path.join(logger.get_dir(), "monitor.json"))
    set_global_seeds(seed)
    env.seed(seed)
    gym.logger.setLevel(logging.WARN)

    if relax:
        policy = RelaxedGaussianMlpPolicy
    else:
        policy = GaussianMlpPolicy
    if endwhendone:
        num_timesteps = 10e9
    learn(env, policy=policy, seed=seed, p_lr=p_lr, vf_lr=vf_lr, l2=l2,
          cv_lr=cv_lr, cv_num=cv_num, gamma=0.99, lam=0.97, score=score, 
          timesteps_per_batch=2500, desired_kl=0.002, logdir=logdir, 
          num_timesteps=num_timesteps, animate=False, var_check=var_check,
          endwhendone=endwhendone)

    env.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Mujoco benchmark.')
    parser.add_argument('--logdir', help='logdir', default=None)
    parser.add_argument('--seed', help='RNG seed', type=int, default=0)
    parser.add_argument('--env', help='environment ID', type=str, default="InvertedPendulum-v1")
    parser.add_argument('--relax', type=str, help='relax or a2c', default="False")
    parser.add_argument('--numt', help='num timesteps', type=int, default=1e6)
    parser.add_argument('--checklogdir', type=str, help='whether to check if logdir exists', default="False")
    parser.add_argument('--p_lr', help='policy learning rate', type=float, default=0.0001)
    parser.add_argument('--vf_lr', help='value-function learning rate', type=float, default=0.001)
    parser.add_argument('--cv_lr', help='control-variate learning rate', type=float, default=0.001)
    parser.add_argument('--endwhendone', type=str, help='stop training when done', default="False")
    parser.add_argument('--score', help='target score', type=float, default=9100.0)  
    parser.add_argument('--cv_num', help='number of times to train cv', type=int, default=25)
    parser.add_argument('--var_check', type=str, help='whether to output logvariance', default="False")
    parser.add_argument('--l2', type=str, help='whether to use l2 loss for cv optim', default="True")
    
    args = parser.parse_args()
    
    if args.checklogdir=="True":
        assert not os.path.exists(args.logdir)    
    logger.configure(args.logdir, format_strs=["stdout", "log", "tensorboard", "json"])
    train(args.env, num_timesteps=args.numt, seed=args.seed, logdir=args.logdir, 
          relax=(args.relax=="True"), p_lr=args.p_lr, vf_lr=args.vf_lr, cv_lr=args.cv_lr, 
          cv_num=args.cv_num, endwhendone=(args.endwhendone=="True"), score=args.score, 
          var_check=(args.var_check=="True"), l2=(args.l2=="True"))
