#!/usr/bin/env python3
import os
import re
import sys
import argparse
import subprocess
import urllib.parse

import requests
from dotenv import load_dotenv


def load_env(env_file:str):
  """
  Load environment variables from .env file.
  
  Parameters: 
  env_file(str): Path to .env file
  """
  load_dotenv(dotenv_path=env_file)

def get_github_user(token:str) -> str:
  """
  Get GitHub username from GitHub API.
  
  Parameters:
  token(str): GitHub access token
  
  Returns:
  str: GitHub username
  
  Raises:
  Exception: If GitHub API returns an error
  """
  headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {token}',
    'X-GitHub-Api-Version': '2022-11-28' 
  }
  
  response = requests.get('https://api.github.com/user', headers=headers)
  if response.status_code == 200:
    return response.json()['login']
  else:
    raise Exception(f"Error: {response.status_code} - {response.text}")

def get_repos(username:str, token:str) -> list:
  """
  Get all repositories for a GitHub user. 
  
  Parameters:
  username(str): GitHub username
  token(str): GitHub access token
  
  Returns:
  list: List of repositories
  
  """
  print(f"Getting repos for {username} and token {token}")
  headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {token}',
    'X-GitHub-Api-Version': '2022-11-28'
  }
  params = {
    'type': 'all', # all, owner, public, private, member
    'page': 1,
  }
  
  repos = []
  while True:
    # https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repositories-for-the-authenticated-user
    url = f"https://api.github.com/user/repos"
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
      raise Exception(f"Error: {response.status_code}")
    repos += response.json()
    if 'Link' in response.headers and 'rel="next"' in response.headers['Link']: # check if there is a next page
      params['page'] = int(params['page']) + 1 
    else:
      break
  
  return repos

def valid_dir_name(name:str) -> str:
  """
  Validate directory name for a repository.
  
  Parameters:
  name(str): Repository name
  
  Returns:
  str: Valid directory name if name is valid or raises RuntimeError
  """
  if not re.match(r"^[-\.\w]*$", name): # check if name contains only letters, numbers, underscores, periods, and hyphens
      raise RuntimeError("invalid name '{0}'".format(name))
  return name

def create_dir(name:str, permission:int) -> str:
  """
  Create directory if it does not exist with permission.
  
  Parameters:
  name(str): Directory name
  permission(int): Directory permission
  
  Returns:
  str: Directory name if directory is created or raises RuntimeError
  """
  if not os.path.exists(name):
    os.makedirs(name, mode=permission, exist_ok=True)
  return name

def backup_repo(repo_name:str, clone_url:str, save_dir:str, username:str, token:str, sync:bool=False) -> None:
  """
  Backup or sync a GitHub repository.
  
  Parameters:
  repo_name(str): Repository name
  clone_url(str): Repository clone URL
  save_dir(str): Path to save repository
  username(str): GitHub username
  token(str): GitHub access token
  sync(bool): Sync repository if True, otherwise backup repository
  
  Returns:
  None
  """
  message = "Backing up..." if not sync else "Syncing..."
  print(f"{message} {repo_name} from {clone_url} to {save_dir}", file=sys.stderr)
  
  parsed_url = urllib.parse.urlparse(clone_url)
  list_ = list(parsed_url)
  list_[1] = f"{username}:{token}@{parsed_url.netloc}" # replace netloc with username:token@netloc
  repo_url = urllib.parse.urlunparse(list_) # convert list back to url
  save_path = os.path.join(save_dir, repo_name) 
  
  create_dir(save_path, 0o770)
  
  if not sync:
    subprocess.run([
      'git',
      'clone',
      '--quiet',
      repo_url,
    ], cwd=save_path)
  else: 
    subprocess.run([
      'git',
      'init',
      '--bare',
      '--quiet'
    ], cwd=save_path)
    
    subprocess.run([
      'git',
      'fetch',
      '--force',
      '--prune',
      '--tags',
      repo_url,
      'refs/heads/*:refs/heads/*',
      'refs/tags/*:refs/tags/*',
    ], cwd=save_path)
  
def parse_arguments():
  """
  Parse command line arguments.
  
  Parameters:
  None
  
  Returns:
  argparse.Namespace: Parsed arguments
  """
  arg_parser = argparse.ArgumentParser(description="Backup or sync GitHub repositories")
  arg_parser.add_argument('-b', '--backup', action='store_true', help="Backup repositories")
  arg_parser.add_argument('-s', '--sync', action='store_true', help="Sync repositories")
  arg_parser.add_argument('-e', '--env-file', default='.env', required=True, help="Path to .env file")
  
  return arg_parser.parse_args()

  

def main():
  args = parse_arguments()
  load_dotenv(dotenv_path=args.env_file)
  token = os.getenv('GITHUB_ACCESS_TOKEN')
  sync = True if args.sync else False
  username = get_github_user(token)
  save_dir = os.getenv('SAVE_DIR')
  save_path = os.path.expanduser(save_dir)
  if create_dir(save_path, 0o770):
    print(f"Created directory {save_path}", file=sys.stderr)
  repos = get_repos(username, token)
  
  for repo in repos:
    name = valid_dir_name(repo['name'])
    owner = valid_dir_name(repo['owner']['login'])
    save_path = os.path.join(save_dir, owner)
    create_dir(save_path, 0o770)
    clone_url = repo['clone_url']
    backup_repo(name, clone_url, save_path, username, token, sync)

if __name__ == '__main__':
  main()