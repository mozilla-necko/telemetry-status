import json

# Read probe names from probes.txt
# We want a list of probe names we're interested in
# TODO: we could change this to be all the probes that have necko@mozilla.com in the email list instead.
with open('probes.txt', 'r') as f:
    probe_names = []
    for line in f:
        line = line.strip()
        if not line or line.startswith('//') or line.startswith('#'):
            continue
        probe_names.append(line)

# Open all_probes.json
# This file contains a JSON used in https://probes.telemetry.mozilla.org/

# fetch https://probeinfo.telemetry.mozilla.org/firefox/all/main/all_probes and load as json
import requests
response = requests.get('https://probeinfo.telemetry.mozilla.org/firefox/all/main/all_probes')
all_probes = response.json()

# https://hg.mozilla.org/mozilla-central/raw-file/tip/toolkit/components/telemetry/Histograms.json
response = requests.get('https://hg.mozilla.org/mozilla-central/raw-file/tip/toolkit/components/telemetry/Histograms.json')
histograms = response.json()

# TODO: process scalars.yaml
# TODO: process events.yaml

def process_json(key, value, out_file):
    optout = False
    firstVersion = "?"
    lastVersion = "?"

    firstVersion = value["history"]["nightly"][-1]["versions"]["first"]

    # TODO: this only works for histograms
    for k, v in histograms.items():
        if k == key:
            lastVersion = v["expires_in_version"]
            if "releaseChannelCollection" in v and v["releaseChannelCollection"] == "opt-out":
                optout = True
            break

    out_file.write(f"{key},{optout},{firstVersion},{lastVersion}\n")

with open("out.csv", "w") as out_file:
    out_file.write(f"probe name, release, first version, last version\n")
    for name in probe_names:
        for key, value in all_probes.items():
            if value["name"] == name:
                process_json(name, value, out_file)
                break
