# Docker and Kubernetes — A Practical Beginner-Friendly Guide

## 1. The Simple Idea

The easiest way to understand the difference is:

- **Docker** packages an application together with the environment it needs so it can run consistently.
- **Kubernetes** manages many containers across one or more servers.

A simple analogy:

> **Docker = a standardized box that contains an application and everything it needs to run.**  
> **Kubernetes = the manager that organizes, restarts, scales, and distributes many of those boxes.**

---

# 2. Why Docker Exists

Without Docker, an application may depend on many things installed directly on a computer:

- a specific Python version,
- specific system libraries,
- a specific Chrome version,
- environment variables,
- package versions,
- Linux tools,
- system configuration.

This often causes the classic problem:

> “It works on my computer, but not on yours.”

For example:

```text
Computer A
├── Python 3.11
├── Chrome version X
├── Library version A
├── Package version B
└── Application

Computer B
├── Python 3.10
├── Different Chrome version
├── Different libraries
└── Same application
```

The same application may behave differently because the environments are different.

Docker reduces this problem by packaging the application together with its required runtime environment.

```text
┌────────────────────────────┐
│ Docker Container           │
│                            │
│ Application                │
│ Python / runtime           │
│ Required libraries         │
│ Configuration              │
│ Supporting tools           │
│                            │
└────────────────────────────┘
```

The idea is:

> If the Docker environment is the same, the application should behave much more consistently across machines.

---

# 3. Docker Image vs Docker Container

This is one of the most important concepts.

## Docker Image

A **Docker image** is a packaged template.

It contains the application and the files needed to create a running environment.

You can think of it as:

- an installation package,
- a blueprint,
- a frozen application environment.

Example:

```text
BEX Docker Image
```

This is not necessarily running yet.

## Docker Container

A **container** is a running instance of a Docker image.

```text
Docker Image
     ↓
   Run
     ↓
Docker Container
```

Simple analogy:

```text
Docker Image     = game installation package
Docker Container = the game currently running
```

Another analogy:

```text
Docker Image = a mold
Container    = an object created from that mold
```

A single image can be used to create several containers:

```text
                 ┌── Container 1
Docker Image ────┼── Container 2
                 └── Container 3
```

---

# 4. What Is a Dockerfile?

A **Dockerfile** is a recipe for building a Docker image.

Conceptually, it may say:

```dockerfile
FROM ubuntu

# Install runtime
RUN install python

# Install dependencies
RUN install required libraries

# Copy application files
COPY my_program /app

# Start the application
CMD run my_program
```

In plain English:

```text
Start with Ubuntu
        ↓
Install Python
        ↓
Install required libraries
        ↓
Copy my application
        ↓
Define how to start it
        ↓
Build Docker Image
```

So:

> **Dockerfile = instructions for creating a Docker image.**

---

# 5. What Is Docker Compose?

A real project may need more than one container.

For example:

```text
API server
Database
Worker
Browser runner
Cache
```

Instead of starting each container separately, **Docker Compose** lets you describe the whole group and start it with one command.

For example:

```bash
docker compose up
```

A useful analogy:

> **Docker manages individual workers.**  
> **Docker Compose starts the whole team together.**

For a project such as BEX, a command like:

```bash
docker compose up --build -d challenge-api
```

roughly means:

> Build the required Docker environment and start the `challenge-api` service in the background.

---

# 6. What Does `--build` Mean?

When you run:

```bash
docker compose up --build
```

Docker rebuilds the image before starting the container.

This is important when application files or source code have changed.

For example:

```text
Edit JavaScript detector
        ↓
docker compose up --build
        ↓
New image is built
        ↓
Container starts using new code
```

Without rebuilding, the running container may still use an older copy of the code.

---

# 7. What Does `-d` Mean?

The `-d` option means **detached mode**.

Example:

```bash
docker compose up -d
```

This runs containers in the background.

Without `-d`, the container logs remain attached to the current terminal.

You can later inspect logs with:

```bash
docker compose logs -f
```

---

# 8. What Is Kubernetes?

Docker can run containers, but large production systems may have hundreds or thousands of containers.

Imagine a company running:

```text
100 web containers
50 API containers
30 AI worker containers
20 background-service containers
```

Managing them manually becomes difficult.

Questions appear constantly:

- What happens if a container crashes?
- What if one server fails?
- What if traffic suddenly increases?
- Which server should run which container?
- How should a new version be deployed?
- How should traffic be routed?

This is where **Kubernetes** becomes useful.

---

# 9. Kubernetes in Simple Terms

Kubernetes automatically manages containers across servers.

```text
                    Kubernetes
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Server 1      Server 2      Server 3
          │             │             │
      Containers     Containers     Containers
```

Kubernetes watches the system and tries to keep the desired state running.

For example:

```text
Desired state:
5 API containers
```

If one crashes:

```text
5 running
   ↓
1 crashes
   ↓
4 running
   ↓
Kubernetes detects failure
   ↓
starts a replacement
   ↓
5 running again
```

---

# 10. What Kubernetes Commonly Does

Kubernetes can automatically handle:

- restarting failed containers,
- scaling the number of containers,
- distributing containers across servers,
- load balancing,
- service discovery,
- rolling deployments,
- rollbacks,
- configuration management,
- secrets management,
- networking,
- health checking.

---

# 11. Scaling Example

Suppose your service normally needs three containers.

```text
Normal traffic

Container 1
Container 2
Container 3
```

Traffic becomes very high.

Kubernetes can scale the system:

```text
High traffic

Container 1
Container 2
Container 3
Container 4
Container 5
Container 6
Container 7
Container 8
```

When traffic drops, Kubernetes can reduce the number again.

This is called **scaling**.

---

# 12. Docker and Kubernetes Relationship

The basic relationship is:

```text
Application
    ↓
Docker Image
    ↓
Docker Container
    ↓
Kubernetes manages many containers
```

Another analogy:

```text
Docker
= prepares and runs one standardized worker

Kubernetes
= manages a large workforce across many machines
```

Docker and Kubernetes are therefore not competitors in the simple sense.

They solve different levels of the problem.

---

# 13. Docker vs Virtual Machine

Docker containers and virtual machines are often confused.

## Virtual Machine

A VM usually includes an entire guest operating system.

```text
Physical Computer
      ↓
Host OS
      ↓
Virtualization Software
      ↓
Guest Ubuntu OS
      ↓
Application
```

A VM can be relatively heavy because the guest OS itself must run.

## Docker

Docker containers usually share the host system's kernel rather than running a completely separate operating system for every container.

```text
Host OS / Linux Kernel
         ↓
      Docker
         ↓
 ┌───────┼────────┐
 ▼       ▼        ▼
App 1   App 2    App 3
```

This often makes containers:

- faster to start,
- smaller,
- lighter,
- easier to reproduce.

---

# 14. Windows and Docker

On Windows, Linux-based Docker workloads commonly run through **WSL2**.

Typical structure:

```text
Windows
   ↓
WSL2
   ↓
Ubuntu / Linux environment
   ↓
Docker Desktop
   ↓
Docker Containers
```

For Linux-oriented development projects, this is often easier than trying to install every dependency directly into Windows.

---

# 15. What Is WSL2?

WSL2 stands for:

> **Windows Subsystem for Linux 2**

It allows Windows users to run a real Linux environment conveniently.

For development, it lets you use commands such as:

```bash
git
ls
cd
curl
docker
python
```

inside Ubuntu while still working on a Windows computer.

---

# 16. Why Docker Is Useful for the BEX Challenge

A browser-security challenge such as BEX may depend on:

- a particular Linux environment,
- a specific Chrome version,
- Python services,
- Docker networking,
- exact dependencies,
- challenge configuration.

Installing all of those manually can be difficult.

Docker lets the project maintainers package the expected runtime.

The workflow becomes approximately:

```text
Download project
      ↓
Build Docker image
      ↓
Start challenge container
      ↓
Run local BEX scorer
```

This gives the developer an environment much closer to the expected challenge execution environment.

---

# 17. Docker Compose in BEX

A command such as:

```bash
docker compose up --build -d challenge-api
```

can be understood as:

```text
docker compose
→ use the project's compose configuration

up
→ start the service

--build
→ rebuild the image first

-d
→ run it in the background

challenge-api
→ start this specific service
```

So the full meaning is approximately:

> Build the BEX challenge API Docker environment and start it in the background.

---

# 18. What You Actually Edit

Docker is not the solution itself.

Docker only provides the environment in which the solution runs.

For BEX, your real work is the detector logic, for example JavaScript files such as:

```text
ad_blockers.js
capture_recording.js
developer_tools.js
identity_security.js
media_video.js
network_vpn.js
save_research.js
tabs_workflow.js
```

The flow is:

```text
Edit detector code
       ↓
Rebuild Docker image
       ↓
Run local challenge
       ↓
Get score
       ↓
Improve code
       ↓
Repeat
```

---

# 19. Do You Need Kubernetes for BEX?

For normal local BEX development:

> **No.**

You mainly need:

```text
Windows
   ↓
WSL2
   ↓
Ubuntu
   ↓
Docker Desktop
   ↓
Docker Compose
   ↓
BEX challenge environment
```

Kubernetes is mainly useful when operating a much larger infrastructure, for example:

- many miners,
- many servers,
- a distributed production service,
- automatic scaling,
- large container fleets.

For a single local development machine, Docker Compose is usually enough.

---

# 20. Final Comparison

| Technology | Main Purpose |
|---|---|
| Docker Image | Packaged application environment |
| Docker Container | Running instance of an image |
| Dockerfile | Instructions for building an image |
| Docker Compose | Starts and manages a group of containers |
| WSL2 | Linux environment inside Windows |
| Virtual Machine | Full virtual computer with its own OS |
| Kubernetes | Large-scale automated container management |

---

# 21. One-Sentence Summary

> **Docker packages and runs applications in reproducible containers; Docker Compose manages several containers on one project; Kubernetes manages large numbers of containers across servers; and for local BEX development, Docker/Compose is important while Kubernetes is not currently necessary.**
