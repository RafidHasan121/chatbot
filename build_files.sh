echo "Checking python version.."
python3 --version
echo "Building python project packages.."
python3 -m pipenv install -r requirements.txt
python3 manage.py collectstatic