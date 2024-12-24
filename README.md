<img src=stp_icon.png width=160>

## stp_prio

Python wrapper around the Unifi API to retrieve STP/RSTP priority (and other info such as MAC, model, IP, firmware version) of the USW switches at a site.

### Setup and Usage

Requires a semi-recent Python with the `requests` module installed.

Edit the script to adjust the variables at the top such as site id, Unifi controller hostname, and API login credentials.

Run with `-h` or `--help` for help on the commandline arguments.

### Sample Output

```
device name    prio   type  model    MAC                IP             fw version
─────────────────────────────────────────────────────────────────────────────────────
sw01 - closet  4096   rstp  USPM16P  0c:ea:14:31:af:a2  192.168.20.11  7.1.26.15869
sw02 - desk    8192   rstp  USM25G5  94:2a:6f:7e:4c:66  192.168.20.12  2.1.4.955
sw03 - desk    12288  rstp  USL8LPB  f4:e2:c6:53:1e:f6  192.168.20.13  7.1.26.15869
```

### List of Environment Variables

- `UNIFI_HOST` the hostname and port of your Unifi controller e.g. `unifi.foo.com:8443`
- `UNIFI_USER` a user to authenticate with for API calls (typically `admin`)
- `UNIFI_PASS` password (_yes_ I know it's not a good idea to store passwords in the clear! Please fork the script and improve the security by using a password manager, cryptography or whatever other method you see fit!)

### Other Variables (hardcoded)

Can be overridden using argument `--site/-s`.

- `DEFAULT_SITE` = The default site to operate on (you will see this if you navigate to your Unifi controller, it is the part after the `/manage/` in the URL)

### Example Helper Script

Here's a small helper script example for storing credentials and vars in a separate file:

```
#!/bin/sh

export UNIFI_HOST=unifi.mycorp.net:8443
export UNIFI_USER=admin
export UNIFI_PASS=supersecret123

/usr/local/bin/stp_prio.py \
  --site ioj7qtxy \
  "$@"
```

### Can this program do _xyz_ ?

I wrote this to scratch my own itch. I've tested it fairly extensively on my own setup, but YMMV. I am running UNA version 9.0.106 as of this writing. Bugreports or PRs to add features welcome!

### See Also

- [luckman212/unifi-usp-control](https://github.com/luckman212/unifi-usp-control) - Control or retrieve status of a USP-Plug device
