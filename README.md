# nfa

This is nfa or [nfstream]() for [Arkime](https://www.arkime.com). It's a simple demo program to use nfstream to check a pcap from Arkime based on id or rootId. It has only been tested on Arkime v2.7.1 and v3.0.0 running on Ubuntu 18.04 LTS with python 3.8.

## Installation

If you don't have python3.8 and python3.8-venv installed you can use **make apt-install** to install them and curl used to get static files. Then run the following command to install requiered Python packages and get local copies of swagger and redoc.

    make install

The **install** targets comments one line in the nfstream source code to make everything work. If you have a better solution please create an issue on GitHub.

Copy the default configuration and change the default values.

    cp config-default.ini config.ini
    $EDITOR config.ini

## Usage

Run it for "production" use, binds to all interfaces,  with

    make run

or with binding to 127.0.0.1 and with reloads based on changed files

    make development

Enable it via Wise or config.ini.

    [right-click]
    NFA=url:http://<hostname>:5001/visual_rootid/%ID%?start=%ISOSTART%&stop=%ISOSTOP%&node=%NODE%;name:nfa;category:ip

## Example output

Below is an example output from the pcap 2021-09-22-Squirrelwaffle-with-Qakbot-and-Cobalt-Strike.pcap.zip available from from https://www.malware-traffic-analysis.net/2021/09/22/index.html.

{
    "id":0,
    "expiration_id":0,
    "src_ip":"172.16.1.128",
    "src_mac":"00:08:02:1c:47:ae",
    "src_oui":"00:08:02",
    "src_port":53016,
    "dst_ip":"103.253.212.72",
    "dst_mac":"20:e5:2a:b6:93:f1",
    "dst_oui":"20:e5:2a",
    "dst_port":80,
    "protocol":6,
    "ip_version":4,
    "vlan_id":0,
    "tunnel_id":0,
    "bidirectional_first_seen_ms":1632336810731,
    "bidirectional_last_seen_ms":1632336812131,
    "bidirectional_duration_ms":1400,
    "bidirectional_packets":9,
    "bidirectional_bytes":1216,
    "src2dst_first_seen_ms":1632336810731,
    "src2dst_last_seen_ms":1632336812131,
    "src2dst_duration_ms":1400,
    "src2dst_packets":5,
    "src2dst_bytes":504,
    "dst2src_first_seen_ms":1632336811135,
    "dst2src_last_seen_ms":1632336812130,
    "dst2src_duration_ms":995,
    "dst2src_packets":4,
    "dst2src_bytes":712,
    "application_name":"HTTP",
    "application_category_name":"Web",
    "application_is_guessed":0,
    "requested_server_name":"sukmabali.com",
    "client_fingerprint":"",
    "server_fingerprint":"",
    "user_agent":"",
    "content_type":"text/html"
}
