#!/usr/bin/env python3
"""Builds the submission report as a self-contained HTML file (images inlined)."""
import base64, html, pathlib, re

DOCS = pathlib.Path(__file__).parent
ROOT = DOCS.parent

def img(name):
    data = base64.b64encode((DOCS / name).read_bytes()).decode()
    return f"data:image/jpeg;base64,{data}"

def figure(name, caption):
    return f'<figure><img src="{img(name)}" alt="{html.escape(caption)}"><figcaption>{html.escape(caption)}</figcaption></figure>'

def code(path, start=None, end=None, grep=None, maxlines=None):
    text = (ROOT / path).read_text(errors="replace")
    lines = text.splitlines()
    if grep:
        lines = [l for l in lines if re.search(grep, l)]
    if start is not None:
        lines = lines[start:end]
    if maxlines:
        lines = lines[:maxlines]
    return html.escape("\n".join(lines))


def sg_table():
    import json
    rules = json.load(open(ROOT / "docs/evidence/security-group-rules.json"))["SecurityGroupRules"]
    def key(r):
        return (r["IsEgress"], r.get("FromPort") or 0)
    rows = []
    for r in sorted(rules, key=key):
        direction = "Egress" if r["IsEgress"] else "Ingress"
        proto = r["IpProtocol"]
        if proto == "-1":
            ports, proto = "all", "all"
        elif r["FromPort"] == r["ToPort"]:
            ports = str(r["FromPort"])
        else:
            ports = f'{r["FromPort"]}-{r["ToPort"]}'
        src = r.get("CidrIpv4") or (r.get("ReferencedGroupInfo") or {}).get("GroupId", "")
        if src == "sg-0fcc9192f27c43745":
            src = "this security group"
        rows.append(
            f"<tr><td>{direction}</td><td><code>{ports}</code></td><td>{proto}</td>"
            f"<td><code>{html.escape(src)}</code></td><td>{html.escape(r.get('Description',''))}</td></tr>"
        )
    return ("<table><tr><th>Direction</th><th>Port</th><th>Protocol</th>"
            "<th>Source / destination</th><th>Description</th></tr>" + "".join(rows) + "</table>")


def template_excerpt():
    """A contiguous slice of the user-data template, with Terraform's $$ escapes
    resolved so it reads as the script that actually runs on the instance."""
    text = (ROOT / "terraform/user_data.sh.tftpl").read_text()
    start = text.index("run_backend() {")
    end = text.index("# --- 7. Smoke test")
    body = text[start:end].replace("$${", "${").rstrip()
    return html.escape(body)

body = f"""
<div class="title-block">
  <h1>Deploying a Multi-Service Node.js E-commerce Application</h1>
  <p class="subtitle">Using Terraform and Docker on AWS</p>
  <p class="meta">
    <b>Submitted by:</b> Sagar Rathore &nbsp;·&nbsp;
    <b>Date:</b> 17 October 2026 &nbsp;·&nbsp;
    <b>Region:</b> ap-south-1 &nbsp;·&nbsp;
    <b>AWS account:</b> 111122223333<br>
    <b>Docker Hub:</b> saagarsaga &nbsp;·&nbsp;
    <b>Terraform:</b> v1.16.6 &nbsp;·&nbsp;
    <b>AWS provider:</b> ~&gt; 5.60
  </p>
</div>

<h2>1. Objective and outcome</h2>
<p>Provision AWS infrastructure with Terraform and deploy five Dockerized Node.js
services — four backends (user, products, orders, cart) and one frontend — onto an
EC2 instance, with the frontend publicly accessible.</p>
<p><b>Outcome:</b> <span class="ok">Completed.</span> All five images were built, pushed to
Docker Hub and deployed by a single <code>terraform apply</code>. The frontend served
"Frontend is Live" at <code>http://13.234.113.72</code> with all four backends reporting
healthy, while backend ports 3001–3004 were verified unreachable from the internet.</p>

<table>
  <tr><th style="width:38%">Deliverable</th><th>Result</th></tr>
  <tr><td>5 Dockerfiles, built and tested locally</td><td class="ok">Done — all 6 endpoint checks passed</td></tr>
  <tr><td>Images tagged and pushed to Docker Hub</td><td class="ok">Done — 5 public repos, linux/amd64 + linux/arm64</td></tr>
  <tr><td>VPC with a public subnet</td><td class="ok">Done — vpc-0b28f142d2d1b77d3, 10.20.0.0/16</td></tr>
  <tr><td>EC2 instance hosting the containers</td><td class="ok">Done — i-05f47627413ac11b3, t3.micro, Ubuntu 22.04</td></tr>
  <tr><td>Security groups (public 80/3000, internal 3001–3004)</td><td class="ok">Done — sg-0fcc9192f27c43745, externally verified</td></tr>
  <tr><td>Docker installed and containers run via user-data</td><td class="ok">Done — see the console log in section 6</td></tr>
  <tr><td>Frontend publicly accessible</td><td class="ok">Done — HTTP 200, homepage renders</td></tr>
  <tr><td>Public IP / DNS printed as a Terraform output</td><td class="ok">Done — 11 outputs, section 5</td></tr>
</table>

<h2>2. Architecture</h2>
<div class="ascii">                        Internet
                            |
                   :80 / :3000 (public)
                            |
+---------------------------|-----------------------------------------+
| VPC  10.20.0.0/16         |                                          |
|                           |                                          |
|  +-- Public subnet 10.20.1.0/24 (ap-south-1a) --------------------+  |
|  |                        |                                       |  |
|  |   +-- EC2  t3.micro - Ubuntu 22.04 - 10.20.1.86 -------------+ |  |
|  |   |                    |                                     | |  |
|  |   |   +----------------v-------------+                       | |  |
|  |   |   | frontend          :3000      |  published as :80     | |  |
|  |   |   +-------+----------------------+                       | |  |
|  |   |           | docker network "shopkart-net"                | |  |
|  |   |   +-------+----+------------+------------+               | |  |
|  |   |   v            v            v            v               | |  |
|  |   | user:3001  products:3002  orders:3003  cart:3004         | |  |
|  |   +----------------------------------------------------------+ |  |
|  +----------------------------------------------------------------+  |
|   Internet Gateway  -  Public route table  -  Security group          |
+-----------------------------------------------------------------------+</div>
<p>The frontend reaches each backend by container name over the private Docker bridge
network, so no backend port needs to be exposed publicly. The security group permits
3001–3004 only from members of the group itself.</p>

<h2>3. Application and containerisation</h2>
<p>Each service is an Express app returning the sample response required by the brief,
plus a <code>/health</code> endpoint and a demo data endpoint.</p>
<table>
  <tr><th>Service</th><th>Port</th><th>Sample response</th><th>Endpoints</th></tr>
  <tr><td>user-service</td><td>3001</td><td><code>user Service Running</code></td><td>/, /health, /users</td></tr>
  <tr><td>products-service</td><td>3002</td><td><code>products Service Running</code></td><td>/, /health, /products</td></tr>
  <tr><td>orders-service</td><td>3003</td><td><code>orders Service Running</code></td><td>/, /health, /orders</td></tr>
  <tr><td>cart-service</td><td>3004</td><td><code>cart Service Running</code></td><td>/, /health, /cart</td></tr>
  <tr><td>frontend</td><td>3000 &rarr; 80</td><td>"Frontend is Live" page</td><td>/, /health, /api/status, /api/&#123;service&#125;</td></tr>
</table>

<h3>Dockerfile (user-service, representative of all five)</h3>
<pre>{code('services/user-service/Dockerfile')}</pre>
<p>Design choices: <code>node:20-alpine</code> for a small image (199 MB); manifests copied
before source so the dependency layer caches; <code>npm ci</code> against a committed
lockfile for reproducibility; the container runs as the unprivileged <code>node</code>
user; and a <code>HEALTHCHECK</code> lets Docker Compose gate startup ordering.</p>

<h3>Local build and test</h3>
<p><code>scripts/build-and-test.sh</code> builds all five images, starts them with Docker
Compose and asserts every endpoint:</p>
<pre class="light">==&gt; Endpoint checks
OK      user-service       http://localhost:3001/
OK      products-service   http://localhost:3002/
OK      orders-service     http://localhost:3003/
OK      cart-service       http://localhost:3004/
OK      frontend page      http://localhost:8080/
OK      aggregated state   http://localhost:8080/api/status</pre>
{figure('frontend-local.jpg', 'Figure 1 — The stack running locally under Docker Compose, 4/4 backends healthy.')}

<h3>Publishing to Docker Hub</h3>
<p>Images were built with <code>docker buildx</code> for <code>linux/amd64</code> and
<code>linux/arm64</code>. This matters: the build host is an Apple Silicon Mac, so a plain
<code>docker build</code> would have produced arm64-only images that a t3.micro cannot run.
The amd64 variant was verified locally before pushing (<code>uname -m</code> inside the
container returned <code>x86_64</code> and the service answered correctly).</p>
{figure('dockerhub-repos.jpg', 'Figure 2 — The five public repositories on Docker Hub.')}

<div class="page-break"></div>
<h2>4. Infrastructure provisioning with Terraform</h2>
<p>The configuration is split by concern: <code>network.tf</code>, <code>security.tf</code>,
<code>ec2.tf</code>, <code>variables.tf</code>, <code>outputs.tf</code>, plus the
<code>user_data.sh.tftpl</code> template. <code>terraform validate</code> passes and
<code>terraform fmt -check</code> is clean.</p>

<h3>Resources created (14)</h3>
<table>
  <tr><th>Resource</th><th>Purpose</th></tr>
  <tr><td><code>aws_vpc.main</code></td><td>VPC 10.20.0.0/16, DNS support and hostnames enabled</td></tr>
  <tr><td><code>aws_internet_gateway.main</code></td><td>Internet access for the public subnet</td></tr>
  <tr><td><code>aws_subnet.public</code></td><td>10.20.1.0/24 in ap-south-1a, auto-assigns public IPs</td></tr>
  <tr><td><code>aws_route_table.public</code> + association</td><td>Default route 0.0.0.0/0 to the internet gateway</td></tr>
  <tr><td><code>aws_security_group.app</code></td><td>Frontend and inter-service access control</td></tr>
  <tr><td>6 &times; <code>aws_vpc_security_group_ingress_rule</code></td><td>80, 3000 public; 3001–3004 group-internal</td></tr>
  <tr><td><code>aws_vpc_security_group_egress_rule.all</code></td><td>Outbound for apt and Docker Hub pulls</td></tr>
  <tr><td><code>aws_instance.app</code></td><td>Ubuntu 22.04 t3.micro, encrypted gp3 root, IMDSv2 required</td></tr>
</table>

<h3>Security group design</h3>
<p>The four backend rules use <code>referenced_security_group_id</code> pointing at the group
itself rather than a CIDR, so 3001–3004 are reachable only from inside the group. This is
what makes the "internal communication between services" requirement real rather than
nominal — section 6 shows those ports refusing connections from the internet.</p>
{sg_table()}

<h3>User-data: Docker install and container deployment</h3>
<p>The rendered script performs seven steps: wait for cloud-init's apt locks; install Docker
Engine from Docker's official apt repository (GPG key plus signed source list); enable the
service; create the <code>shopkart-net</code> bridge network; pull all five images; run the
four backends and the frontend with <code>--restart unless-stopped</code>; and finally run a
smoke test against every <code>/health</code> endpoint, writing the result to
<code>/home/ubuntu/deployment-status.txt</code>.</p>
<pre>{template_excerpt()}</pre>
<p class="meta">Excerpt from <code>terraform/user_data.sh.tftpl</code>, shown as rendered (Terraform's <code>$$</code> escapes resolved).</p>

<div class="page-break"></div>
<h2>5. Deployment</h2>
<pre class="light">$ terraform init &amp;&amp; terraform plan -out=tfplan &amp;&amp; terraform apply tfplan

aws_instance.app: Creation complete after 13s [id=i-05f47627413ac11b3]

Apply complete! Resources: 14 added, 0 changed, 0 destroyed.</pre>

<h3>Terraform outputs</h3>
<pre class="light">{code('docs/terraform-outputs.txt')}</pre>

<h3>Provisioned resources, confirmed via the AWS API</h3>
<pre class="light">{code('docs/evidence/vpc.txt')}</pre>
<pre class="light">{code('docs/evidence/subnet.txt')}</pre>
<pre class="light">{code('docs/evidence/instance.txt')}</pre>

<div class="page-break"></div>
<h2>6. Verification</h2>

<h3>6.1 Public frontend access</h3>
{figure('frontend-aws.jpg', 'Figure 3 — The frontend served from the EC2 public IP, reporting 4/4 backends healthy.')}

<h3>6.2 Backend services responding through the frontend</h3>
{figure('frontend-aws-sampledata.jpg', 'Figure 4 — Live JSON from the user and products services, proxied over the private Docker network.')}

<h3>6.3 Endpoint checks</h3>
<pre class="light">GET http://13.234.113.72/              -&gt; "Frontend is Live" homepage
GET http://13.234.113.72/api/status    -&gt; 4/4 backends healthy
GET http://13.234.113.72:3000/health   -&gt; HTTP 200
GET http://13.234.113.72/api/user      -&gt; 3 users
GET http://13.234.113.72/api/products  -&gt; 4 products
GET http://13.234.113.72/api/orders    -&gt; 3 orders
GET http://13.234.113.72/api/cart      -&gt; 2 carts

Backend ports probed from the public internet (must be refused):
  :3001 blocked    :3002 blocked    :3003 blocked    :3004 blocked</pre>
<p>The last block is the security-group evidence: the backends are running and answering the
frontend, yet their ports are not reachable from outside the group.</p>

<h3>6.4 Containers running on the instance</h3>
<p>Captured from the EC2 serial console, which records the user-data run. No SSH key was
configured, so this is the deployment's own log rather than an interactive session:</p>
<pre>{code('docs/evidence/user-data-deployment.log', grep=r'(deployment status|^OK |^NAMES|^frontend |^cart-service|^orders-service|^products-service|^user-service|deployment finished)', maxlines=16)}</pre>

<h3>6.5 Docker installation and image pulls</h3>
<pre>{code('docs/evidence/user-data-deployment.log', grep=r'(Docker installed|Docker network ready|Pulling saagarsaga|Status: Downloaded)', maxlines=16)}</pre>

<div class="page-break"></div>
<h2>7. Security notes</h2>
<ul>
  <li>Backend ports 3001–3004 accept traffic only from the security group itself; verified
      externally as refused.</li>
  <li>No SSH ingress rule is created unless <code>allowed_ssh_cidr</code> is set explicitly;
      this deployment ran with no SSH exposure at all.</li>
  <li>IMDSv2 is required on the instance and the root EBS volume is encrypted.</li>
  <li>Containers run as a non-root user with <code>--restart unless-stopped</code>.</li>
  <li><code>allowed_http_cidr</code> was narrowed from <code>0.0.0.0/0</code> to a single /32
      after the public-access evidence above was captured, so the frontend was not left open
      to the internet.</li>
  <li>The Docker Hub token path is optional and unused here: the images are public, which
      keeps credentials out of user-data (readable through the metadata service).</li>
</ul>

<h2>8. Teardown</h2>
<p>Every resource lives inside the dedicated VPC, so a single command removes all 14 and
leaves nothing behind:</p>
<pre class="light">$ cd terraform &amp;&amp; terraform destroy</pre>

<h2>9. Mapping to the evaluation criteria</h2>
<table>
  <tr><th style="width:42%">Criterion</th><th style="width:10%">Marks</th><th>Evidence</th></tr>
  <tr><td>VPC, subnet and security group setup</td><td class="marks">10</td>
      <td><code>network.tf</code>, <code>security.tf</code>; sections 4 and 5</td></tr>
  <tr><td>EC2 provisioning with Docker setup</td><td class="marks">10</td>
      <td><code>ec2.tf</code> and user-data steps 1–2; section 6.5</td></tr>
  <tr><td>Container deployment via user-data</td><td class="marks">10</td>
      <td>User-data steps 3–7; section 6.4</td></tr>
  <tr><td>Public access to the frontend</td><td class="marks">10</td>
      <td>Figures 3 and 4; section 6.3</td></tr>
  <tr><td>Documentation</td><td class="marks">10</td>
      <td>This report, the repository README and inline comments throughout</td></tr>
</table>

<h2>Appendix — repository layout</h2>
<pre class="light">.
|-- README.md                    full setup, deploy and troubleshooting guide
|-- docker-compose.yml           local build-and-test harness
|-- docs/                        this report and all captured evidence
|-- scripts/
|   |-- build-and-test.sh        build 5 images, run them, assert endpoints
|   `-- push-images.sh           multi-arch buildx build and push
|-- services/
|   |-- user-service/            server.js, package.json, Dockerfile
|   |-- products-service/
|   |-- orders-service/
|   |-- cart-service/
|   `-- frontend/                + public/index.html
`-- terraform/
    |-- versions.tf  provider.tf  variables.tf
    |-- network.tf   security.tf  ec2.tf
    |-- user_data.sh.tftpl       Docker install + container deployment
    |-- outputs.tf               public IP / DNS / URLs
    `-- terraform.tfvars.example</pre>
"""

css = (DOCS / "report.css").read_text()
out = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Deployment Report — Multi-Service Node.js E-commerce on AWS</title>
<style>{css}</style></head><body>{body}</body></html>"""

(DOCS / "DEPLOYMENT-REPORT.html").write_text(out)
print(f"HTML written: {len(out):,} bytes")
