sync:
	fswatch -o /Users/jasonbenn/code/mle-tutor | xargs -n1 -I{} make sync_once

sync_once:
	rsync --delete -azv --exclude 'venv' --exclude '.git' /Users/jasonbenn/code/mle-tutor/ jason:/opt/mle-tutor/
