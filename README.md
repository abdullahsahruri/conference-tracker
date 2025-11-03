# Conference Tracker - One Command

## Add Conference

```bash
./add ISCA 2026 https://iscaconf.org/isca2026/submit/papers.php
```

AI extracts → Database updated → Website pushed!

## Clear All Conferences

```bash
./clear
```

Empties database and pushes to website.

## Examples

```bash
./add ISCA 2026 https://iscaconf.org/isca2026/submit/papers.php
./add MICRO 2026 https://microarch.org/micro58/submit/papers.php
./add DAC 2026 https://dac.com/2026/cfp
```

## View/Manage

```bash
python3 manual_add_conference.py
```

Website: https://abdullahsahruri.github.io/conferences/
