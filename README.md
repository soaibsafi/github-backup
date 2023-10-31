# Github Backup
A simple script to backup all your github repositories. It will create a folder for each repository and clone it into it.

## Usage
### CLI
- Clone the repository: `git clone https://github.com/soaibsafi/github-backup.git`
- Install the dependencies: `pip install -r requirements.txt`
- Copy the `.env.example` file to `.env` and add the required values: `cp .env.example .env`
  - `GITHUB_ACCESS_TOKEN`: Your github token
  - `BACKUP_DIR`: The directory where you want to backup your repositories
- Run the script: `python github_backup/backup.py -e .env`

### Docker
```bash	
docker run -d \
  --name github-backup \
  --user $(id -u):$(id -g) \
  -v /path/to/backup/dir:/github-backup/backup \
  -e GITHUB_ACCESS_TOKEN=your_github_token \
  -e BACKUP_INTERVAL=86400 \
  ghcr.io/soaibsafi/github-backup:latest
``` 
### Notes
The script clone the repositories as bare repositories. So it doesn't contain any working tree. You can read more about bare repositories [here](https://git-scm.com/book/en/v2/Git-on-the-Server-Getting-Git-on-a-Server).

To create a working tree from a bare repository, you can use the following command:
```bash
git clone --bare /path/to/bare/repo.git /path/to/working/tree
```
## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

