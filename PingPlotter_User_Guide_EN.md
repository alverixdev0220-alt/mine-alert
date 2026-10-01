# PingPlotter User Guide

This guide explains how to use PingPlotter on Windows to trace the network path to a destination and to investigate hops that may not appear in a normal `tracert` result.

## 1. Install PingPlotter

Download and install the Windows version of PingPlotter from the official website.

After installation, start **PingPlotter**.

---

## 2. Basic Route Tracing

In the **Target Name** field at the top of the program, enter the destination.

Example:

```text
google.com
```

Or enter an IP address:

```text
8.8.8.8
```

Then click **Start**.

The result may look like this:

```text
Hop    IP                 Avg       PL%
1      192.168.1.1        1 ms      0
2      10.x.x.x           8 ms      0
3      203.x.x.x          14 ms     0
4      ...                20 ms
5      Destination        25 ms
```

### Meaning of the Main Fields

- **Hop 1**: Usually your router or default gateway
- **Hop 2 and later**: ISP routers or intermediate Internet routers
- **Last Hop**: The destination server
- **Avg**: Average response time
- **PL%**: Packet loss percentage

---

## 3. Using TCP When ICMP Is Blocked

A normal Windows `tracert` may show missing hops when intermediate routers block or ignore ICMP responses.

Example:

```text
1   192.168.1.1
2   * * *
3   * * *
4   142.x.x.x
```

In this situation, you can try **TCP tracing** in PingPlotter.

Go to:

```text
Edit
 ↓
Options
 ↓
Engine
```

Then change:

```text
Packet Type
```

to:

```text
TCP
```

The first time you use TCP mode, PingPlotter may ask you to install its **TCP Helper Service**.

If prompted, select:

```text
Install TCP Helper Now
```

---

## 4. Use TCP Port 443

For websites or HTTPS servers, a common configuration is:

```text
Target: google.com
Packet Type: TCP
Port: 443
```

Then click **Start**.

TCP port 443 is normally used by HTTPS, so tracing with TCP/443 can sometimes reveal hops that do not respond to ICMP-based traceroute probes.

---

## 5. Understanding the Results

Example:

```text
Hop   IP                  Avg     PL%
1     192.168.1.1          1      0
2     10.34.0.1            7      0
3     172.20.15.4         11      0
4     203.0.113.5         19      0
5     142.250.x.x         25      0
```

A simplified interpretation is:

```text
My PC
 │
 ▼
192.168.1.1
Local Router
 │
 ▼
10.34.0.1
ISP Internal Network
 │
 ▼
172.20.15.4
ISP / Carrier Router
 │
 ▼
203.0.113.5
Internet Backbone
 │
 ▼
142.250.x.x
Destination Network
```

---

## 6. When Intermediate Hops Are Missing

Example:

```text
1   192.168.1.1
2   10.0.0.1
3   ----
4   ----
5   203.x.x.x
6   destination
```

Missing hops do not necessarily mean that packets failed to pass through those routers.

The real path may look like this:

```text
2
 ↓
[Router that does not respond]
 ↓
[Router that does not respond]
 ↓
5
```

The routers may forward traffic normally while refusing to answer traceroute-related probes.

Even with TCP/443, if a router does not generate the necessary TTL-expired response, its IP address cannot normally be forced to appear.

---

## 7. Compare ICMP and TCP Results

First run a trace using ICMP:

```text
Packet Type = ICMP
```

Then run another trace using:

```text
Packet Type = TCP
Port = 443
```

For example, ICMP may show:

```text
1   192.168.1.1
2   * * *
3   * * *
4   142.x.x.x
```

while TCP may show:

```text
1   192.168.1.1
2   10.1.24.1
3   72.x.x.x
4   142.x.x.x
```

Therefore, if you want to observe as much of the path as possible, compare the **ICMP and TCP results**.

---

## 8. Common TCP Ports

You can change the TCP port depending on the service running on the destination.

| Service | Port |
|---|---:|
| HTTPS | 443 |
| HTTP | 80 |
| SSH | 22 |
| RDP | 3389 |

Example:

```text
Target: example.com
Packet Type: TCP
Port: 443
```

---

## 9. Recommended First Test

For a simple test, use:

```text
Target:
8.8.8.8

Packet Type:
TCP

Port:
443
```

Then click:

```text
Start
```

---

## 10. Compare With Windows `tracert`

You can also run the Windows command:

```cmd
tracert -d 8.8.8.8
```

The `-d` option disables DNS name resolution and shows IP addresses directly, which usually makes the trace faster and easier to read.

Then compare that result with PingPlotter's TCP/443 trace.

```text
Windows tracert
        +
PingPlotter TCP 443
        ↓
Observe as much of the path to the destination as possible
```

---

## 11. Important Limitations

No traceroute program can guarantee that every physical router between you and the destination will be visible.

Intermediate networks may use technologies or policies such as:

- ICMP filtering
- MPLS
- NAT
- VPNs
- Tunneling
- Load balancing
- Firewalls
- TTL response filtering

Therefore, PingPlotter and other traceroute tools show the **network path that is externally observable**, not necessarily every physical device that carries the traffic.

---

## Recommended Configuration Summary

To observe as much of the route as possible:

```text
1. Start PingPlotter
2. Enter the target
3. Set Packet Type = TCP
4. Set Port = 443
5. Click Start
6. Compare the TCP result with the ICMP result
```

Suggested test targets:

```text
8.8.8.8
```

or:

```text
google.com
```
