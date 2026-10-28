#!/usr/bin/env python3
"""Build the branded MyScoutee infrastructure configuration lab guide."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "MyScoutee_Infrastructure_Config_Lab_Guide_EN.pdf"
LOGO = ROOT / "assets" / "heart.png"

for name, filename in (
    ("Guide", "DejaVuSans.ttf"),
    ("GuideBold", "DejaVuSans-Bold.ttf"),
    ("GuideMono", "DejaVuSansMono.ttf"),
):
    pdfmetrics.registerFont(
        TTFont(name, "/usr/share/fonts/truetype/dejavu/" + filename)
    )

NAVY = colors.HexColor("#17324d")
TEAL = colors.HexColor("#176b87")
INK = colors.HexColor("#1c2633")
MUTED = colors.HexColor("#586675")
SOFT = colors.HexColor("#f3f6f8")
LINE = colors.HexColor("#d9e1e8")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    "BodyGuide", fontName="Guide", fontSize=9, leading=13.5,
    textColor=INK, spaceAfter=8,
))
styles.add(ParagraphStyle(
    "TitleGuide", fontName="GuideBold", fontSize=24, leading=31,
    textColor=NAVY, spaceAfter=13,
))
styles.add(ParagraphStyle(
    "SectionGuide", fontName="GuideBold", fontSize=13.5, leading=18,
    textColor=NAVY, spaceBefore=13, spaceAfter=7,
))
styles.add(ParagraphStyle(
    "KickerGuide", fontName="GuideBold", fontSize=8, leading=12,
    textColor=TEAL, spaceAfter=8,
))
styles.add(ParagraphStyle(
    "SmallGuide", parent=styles["BodyGuide"], fontSize=7.8, leading=11,
    textColor=MUTED,
))
styles.add(ParagraphStyle(
    "CellGuide", parent=styles["BodyGuide"], fontSize=7.7, leading=11,
    spaceAfter=0,
))
styles.add(ParagraphStyle(
    "CodeGuide", fontName="GuideMono", fontSize=7.3, leading=11,
    textColor=NAVY, backColor=SOFT, borderPadding=10,
    spaceBefore=4, spaceAfter=10,
))


def p(value, style="BodyGuide"):
    return Paragraph(value, styles[style])


def table(rows, widths):
    cells = [[p(escape(str(cell)), "CellGuide") for cell in row] for row in rows]
    result = Table(cells, colWidths=widths, hAlign="LEFT", repeatRows=1)
    result.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 0), (-1, 0), SOFT),
        ("LINEBELOW", (0, 0), (-1, -1), 0.35, LINE),
    ]))
    return result


def code(value):
    return Preformatted(value, styles["CodeGuide"])


def frame(canvas, document):
    width, height = A4
    canvas.saveState()
    if document.page == 1:
        canvas.drawImage(str(LOGO), 46, height - 77, width=43, height=43, mask="auto")
        canvas.setFillColor(NAVY)
        canvas.setFont("GuideBold", 20)
        canvas.drawString(95, height - 56, "yScoutee")
        canvas.setFillColor(MUTED)
        canvas.setFont("Guide", 8)
        canvas.drawString(96, height - 70, "Engineering documentation")
    else:
        canvas.setFillColor(NAVY)
        canvas.setFont("GuideBold", 8)
        canvas.drawString(46, height - 35, "MYSCOUTEE  /  ENGINEERING")
    canvas.setStrokeColor(LINE)
    canvas.line(46, 40, width - 46, 40)
    canvas.setFont("Guide", 7.3)
    canvas.drawString(46, 27, "MSC-INF-001  |  Version 1.3.0  |  2026-10-28")
    canvas.drawRightString(width - 46, 27, str(document.page))
    canvas.restoreState()


story = [
    p("INFRASTRUCTURE / CONFIGURATION MANAGEMENT", "KickerGuide"),
    Spacer(1, 30),
    p("Infrastructure Configuration Lab", "TitleGuide"),
    p("One disposable MyScoutee-shaped edge. Two configuration tools. "
      "KVM or VMware as the VM provider."),
    Spacer(1, 22),
    table([
        ["Document control", "Value"],
        ["Document ID / version", "MSC-INF-001 / 1.3.0 / EN"],
        ["Repository", "myscoutee-infra"],
        ["Audience", "Developers and operators learning host configuration management"],
        ["Scope", "Local Ubuntu 22.04 VM, nginx, Ansible and Puppet"],
        ["Data and connectivity", "Synthetic page/status; no MyScoutee backend or user data"],
        ["Integration", "Separate sandbox; no deployment into myscoutee-backend"],
    ], [152, 351]),
    Spacer(1, 20),
    p("Start with the helper", "SectionGuide"),
    code("./setup-vagrant.sh           # user-local Vagrant + QEMU provider\n"
         "./lab.sh up kvm ansible      # QEMU/KVM, no system libvirt\n"
         "./lab.sh verify\n"
         "./lab.sh apply puppet       # converge the same VM with Puppet"),
    p("The host entry point is <b>http://127.0.0.1:18080/</b>. The lab uses "
      "the application's <b>/nginx-health</b> response shape as its concrete "
      "configuration exercise. It is a stand-alone teaching edge, not the "
      "application's production nginx image."),
    p("This guide explains the components, the method, and the terminal output. "
      "Follow the same experiment with either tool and compare the evidence."),
    p("The page at port 18080 shows the configured result. Ansible and Puppet "
      "are controlled here through terminal output from <b>ansible-playbook</b> "
      "and <b>puppet apply</b>; this lab has no management web console. "
      "Separate web consoles exist in Ansible AWX and Puppet Enterprise."),
    PageBreak(),

    p("1. Basic ideas", "TitleGuide"),
    p("Configuration management describes how a machine <b>should</b> look, "
      "then makes its actual state match. A successful run needs two kinds of "
      "evidence: the tool reports what it changed, and an independent check "
      "shows the service behaves as expected."),
    table([
        ["Term", "Meaning in this lab"],
        ["Host / guest", "The host is your computer. The guest is the disposable Ubuntu VM whose nginx configuration is managed."],
        ["Desired state", "nginx is installed and running; the shared site and page have the specified content; the active-tool marker has the selected value."],
        ["Actual state", "The packages, files, service and HTTP response currently present inside the VM."],
        ["Convergence", "A run compares actual state with desired state and fixes differences. The first run usually changes several resources."],
        ["Idempotence", "Running the same declaration again leaves already-correct resources unchanged. Ansible shows changed=0; Puppet prints no resource-change Notice."],
        ["Drift", "A manual or external change that moves the VM away from the declared state, such as replacing the managed HTML page with 'drift'."],
        ["Control / target", "The control side starts the tool. The target is the VM being changed. In this small lab both tools execute inside the target VM."],
    ], [113, 390]),
    p("The browser page is an <b>output</b> to inspect. The tool interface for "
      "this lab is the terminal plus the declarations in the repository. "
      "Ansible AWX and Puppet Enterprise are separate web products."),
    PageBreak(),

    p("2. Components and data flow", "TitleGuide"),
    code("host browser/curl :18080\n"
         "        | Vagrant loopback port forwarding\n"
         "Ubuntu guest :8080 -> nginx -> static lab page / status\n"
         "        ^\n"
         "        | Ansible or Puppet -> same shared files and service"),
    table([
        ["Component", "Job", "Where"],
        ["Vagrant + provider", "Creates the VM with QEMU/KVM, optional libvirt or VMware, syncs source and forwards host port 18080 to guest port 8080.", "Vagrantfile"],
        ["Command wrapper", "Selects a provider and a tool; calls Vagrant up, provision, verify or halt.", "lab.sh"],
        ["Bootstrap", "Installs Ansible, Puppet and curl. Puppet's background agent is disabled for a controlled comparison.", "provision/bootstrap.sh"],
        ["Ansible", "A playbook runs ordered tasks, using modules such as apt, file, copy and service. Here it connects locally inside the VM.", "ansible/site.yml"],
        ["Puppet", "A manifest declares package, file and service resources. puppet apply builds and applies a catalog locally; no Puppet Server is used.", "puppet/site.pp"],
        ["Shared input", "The nginx site, HTML page and synthetic JSON are identical for both tools.", "shared/"],
        ["nginx + verifier", "nginx serves the resulting files; curl and the marker check what actually happened.", "guest :8080 / lab.sh verify"],
    ], [84, 298, 121]),
    p("Why this MyScoutee use case?", "SectionGuide"),
    p("The application gateway already exposes <b>/nginx-health</b> with "
      "<b>UP</b>. The lab reproduces that small operational contract, then "
      "shows how configuration management keeps an edge host converged. "
      "The <b>/lab/status.json</b> endpoint explicitly says its backend is "
      "synthetic. It cannot be used to assess real application readiness."),
    p("A single source for both tools", "SectionGuide"),
    p("Ansible and Puppet read the same files under <b>shared/</b>; the apply "
      "command syncs them into the VM first. Their "
      "declarations differ, but the HTTP result should match. Only one tool "
      "runs at a time; <b>/etc/myscoutee-lab/tool</b> records the last one."),
    PageBreak(),

    p("3. Vagrant and Terraform", "TitleGuide"),
    p("Both can own the <b>VM lifecycle</b>. Neither is Ansible or Puppet: "
      "those two tools configure the guest operating system after it exists. "
      "The choice of VM tool does not change the nginx desired state."),
    table([
        ["Question", "Vagrant in this repository", "Terraform alternative"],
        ["What is declared?", "A disposable local Ubuntu box, provider, memory, forwarded port and provisioners in Vagrantfile.", "Libvirt resources such as VM, volumes and network in .tf files; Terraform tracks their identities in state."],
        ["How is it started?", "./lab.sh up kvm ansible calls vagrant up with the QEMU provider using KVM acceleration.", "terraform plan previews the resource changes; terraform apply creates them."],
        ["How does Ansible run?", "Vagrant calls provision/configure.sh inside the VM; it invokes ansible-playbook with localhost inventory.", "Terraform would create the VM; an explicit SSH/Ansible step or wrapper would then configure it. This repo has no Terraform lab path."],
        ["Local conveniences", "Vagrant configures the rsync folder, SSH access and host port forwarding for this lab.", "Those connections and source transfer would need explicit Terraform/provider and wrapper configuration."],
        ["When useful?", "Quick, disposable local comparison on QEMU/KVM, optional libvirt or VMware Workstation/Fusion.", "When the VM, storage and network should follow an infrastructure plan/state workflow."],
    ], [96, 201, 206]),
    p("The existing MyScoutee Terraform configuration in <b>myscoutee-"
      "microservices/infra/terraform</b> creates a larger, k3s-specific VM. "
      "It is a reference for libvirt patterns, not a dependency of this "
      "sandbox. No Ansible or Puppet change here is applied to "
      "<b>myscoutee-backend</b>."),
    p("Exact chain used by this repository", "SectionGuide"),
    code("./lab.sh up kvm ansible\n"
         "  -> vagrant up --provider=qemu (KVM acceleration)\n"
         "  -> provision/bootstrap.sh (install tools)\n"
         "  -> provision/configure.sh\n"
         "  -> ansible-playbook -i 'localhost,' -c local /vagrant/ansible/site.yml"),
    p("For Puppet, the same chain ends with <b>puppet apply "
      "/vagrant/puppet/site.pp</b>. The earlier direct-QEMU test ran these "
      "same guest scripts before Vagrant was installed. Terraform remains "
      "outside this sandbox."),
    PageBreak(),

    p("4. A repeatable method", "TitleGuide"),
    p("Use the same sequence each time. It separates what the tool <b>says</b> "
      "from what the service <b>does</b>, so a green process exit alone is "
      "never the entire conclusion."),
    table([
        ["Step", "Action", "Evidence to read"],
        ["1. Define", "Read the playbook, manifest and shared files before running.", "Know the expected package, files, service, marker and HTTP response."],
        ["2. Apply", "Run Ansible once on the VM.", "Which tasks say changed? Did any task fail?"],
        ["3. Verify", "Check the marker and call the HTTP endpoints.", "Marker says ansible; /nginx-health says UP; status says synthetic/ready."],
        ["4. Repeat", "Run the same Ansible playbook again.", "changed=0, no failures: the desired state is stable."],
        ["5. Compare", "Apply Puppet twice on the same VM.", "First run may switch the marker; second has no resource-change Notice."],
        ["6. Disturb", "Replace the managed HTML page with 'drift'.", "The browser now shows drift, proving the observed state changed."],
        ["7. Repair", "Apply the selected tool and verify again.", "It reports the page correction; the original page returns."],
    ], [70, 230, 203]),
    p("This method tests <b>convergence</b> (a correction happens), "
      "<b>idempotence</b> (the next run makes no correction), and "
      "<b>observable behavior</b> (nginx serves the expected response). "
      "The active-tool marker changes when switching tools; that single "
      "change is expected even if the nginx content is already identical."),
    PageBreak(),

    p("5. Read the Ansible terminal", "TitleGuide"),
    p("Ansible runs a <b>playbook</b> against an <b>inventory</b>. Here the "
      "inventory is localhost and the connection is local, so the playbook "
      "runs inside the VM. Each named <b>task</b> calls a module to check "
      "and, if needed, change one part of the guest."),
    code("$ ./lab.sh up kvm-local ansible\n"
         "TASK [Install shared lab page] .......... ok: [localhost]\n"
         "TASK [Record active config tool] ....... changed: [localhost]\n"
         "PLAY RECAP\n"
         "localhost : ok=9 changed=1 unreachable=0 failed=0"),
    p("These lines were observed through Vagrant's QEMU/KVM provider on the "
      "local Ubuntu 24.04 box. Only the tool marker needed changing because "
      "the previous demo had already configured nginx. A fresh Bento box "
      "will have more changes on its first run."),
    table([
        ["Output", "How to read it"],
        ["ok: [localhost]", "The task completed and found the resource already correct."],
        ["changed: [localhost]", "The task made a correction. Read the task name to see what was touched."],
        ["ok=9", "Nine tasks completed. This includes tasks that reported changed."],
        ["changed=1", "One task modified the VM: here, the active-tool marker."],
        ["unreachable=0 / failed=0", "The target was reachable and no task failed. This is necessary but does not replace HTTP verification."],
    ], [145, 358]),
    code("$ ./lab.sh apply ansible\n"
         "PLAY RECAP\n"
         "localhost : ok=9 changed=0 unreachable=0 failed=0"),
    p("The repeat has <b>changed=0</b>. The playbook is idempotent for this "
      "state. The command reports configuration work; use <b>./lab.sh "
      "verify</b> to check the served result."),
    PageBreak(),

    p("6. Read the Puppet terminal", "TitleGuide"),
    p("A Puppet <b>manifest</b> declares resources: a package, directories, "
      "files and a service. <b>puppet apply</b> compiles those declarations "
      "into a <b>catalog</b> and applies it locally. This lab has no "
      "Puppet Server, agent polling cycle or Puppet web console."),
    code("$ ./lab.sh apply puppet\n"
         "Notice: Compiled catalog for myscoutee-config-lab.\n"
         "Notice: File[/etc/myscoutee-lab/tool]/content: content changed\n"
         "Notice: Applied catalog in 0.30 seconds"),
    p("These lines were observed through Vagrant on the local box. The catalog "
      "compiled, then Puppet changed the marker from ansible to puppet. Puppet "
      "identifies the exact resource path. Elapsed time varies between runs."),
    code("$ ./lab.sh apply puppet\n"
         "Notice: Compiled catalog for myscoutee-config-lab.\n"
         "Notice: Applied catalog in 0.19 seconds"),
    p("On the repeat, there is no resource-change Notice. That is Puppet's "
      "normal quiet output for already-correct resources; unlike Ansible, "
      "this command does not print a per-task recap by default."),
    p("Read drift repair", "SectionGuide"),
    code("$ ./lab.sh ssh -c 'sudo sh -c \"echo drift > /srv/myscoutee-lab/index.html\"'\n"
         "$ ./lab.sh apply puppet\n"
         "Notice: File[/srv/myscoutee-lab/index.html]/content: content changed"),
    p("The file Notice means Puppet restored the declared HTML. Confirm with "
      "<b>./lab.sh verify</b> or by opening the host page. The lab may also "
      "print a Ruby/Augeas warning on Ubuntu 24.04; the run above still "
      "completed and the service check passed."),
    PageBreak(),

    p("7. Runbook and exercises", "TitleGuide"),
    p("Before starting", "SectionGuide"),
    p("Run <b>./setup-vagrant.sh</b> to install Vagrant 2.4.9 and the QEMU "
      "provider in your user directory. The default <b>kvm</b> path needs "
      "QEMU and access to /dev/kvm, without system libvirt. Optional "
      "<b>libvirt</b> and <b>vmware</b> paths need their own provider plugins "
      "and host services. Reserve about 2 GiB RAM, 15 GiB disk and free port "
      "127.0.0.1:18080; install rsync and curl. On a fresh host, the regular "
      "kvm path downloads roughly 2 GiB for the pinned Bento 202502.21.0 "
      "box, plus Ubuntu packages. Later starts use the cached box. QEMU reads "
      "its libvirt-format disk."),
    code("./setup-vagrant.sh\n"
         "./lab.sh up kvm ansible\n"
         "./lab.sh verify\n"
         "curl -fsS http://127.0.0.1:18080/nginx-health\n"
         "curl -fsS http://127.0.0.1:18080/lab/status.json"),
    p("Only on the machine with the earlier Ubuntu 24.04 demo disk, run "
      "<b>./setup-local-box.sh</b> after stopping that demo VM, then "
      "<b>./lab.sh up kvm-local ansible</b>. This optional local path avoids a "
      "second box download; the normal kvm command is the portable default.",
      "SmallGuide"),
    p("Compare convergence", "SectionGuide"),
    code("./lab.sh apply ansible\n"
         "./lab.sh apply ansible      # expect zero managed changes\n"
         "./lab.sh apply puppet\n"
         "./lab.sh apply puppet       # expect no new changes\n"
         "./lab.sh verify"),
    p("Repair a deliberate drift", "SectionGuide"),
    code("./lab.sh ssh -c 'sudo sh -c \"echo drift > /srv/myscoutee-lab/index.html\"'\n"
         "./lab.sh apply puppet       # or ansible, whichever is active\n"
         "./lab.sh verify"),
    p("The selected tool should restore the page. Reapplying a second time "
      "should leave the managed resources unchanged. Switching tools only "
      "changes the marker when the shared content is already identical."),
    p("Stop or remove", "SectionGuide"),
    code("./lab.sh status\n./lab.sh halt\n./lab.sh destroy     # deletes this lab VM and its guest data"),
    PageBreak(),

    p("8. Validation and boundaries", "TitleGuide"),
    table([
        ["Check", "Expected result"],
        ["GET /nginx-health", "HTTP 200 with body UP followed by a newline"],
        ["GET /lab/status.json", "Synthetic JSON with status ready and backend synthetic"],
        ["GET /", "MyScoutee configuration lab page"],
        ["Tool marker", "Exactly ansible or puppet, matching the last apply"],
        ["Second same-tool apply", "No managed resource changes"],
        ["After page drift + apply", "Original HTML restored"],
    ], [187, 316]),
    p("When a check fails", "SectionGuide"),
    table([
        ["Symptom", "Inspect"],
        ["No Vagrant command", "Run ./setup-vagrant.sh; lab.sh finds its user-local binary."],
        ["QEMU/KVM unavailable", "Check qemu-system-x86_64 and user access to /dev/kvm."],
        ["Optional libvirt unavailable", "Install the libvirt plugin and start the system libvirt service."],
        ["VMware provider unavailable", "Install the VMware provider plugin and utility; verify VMware itself works."],
        ["Guest provisioning failed", "Read Vagrant output, then use ./lab.sh ssh to inspect apt or nginx -t."],
        ["Guest passes, host port fails", "Check port 18080 availability and provider forwarding configuration."],
    ], [175, 328]),
    p("Operating boundary", "SectionGuide"),
    p("The lab manages only its disposable guest. It has no TLS, domain, "
      "secrets, backend proxy routes, production images, monitoring integration "
      "or persistent MyScoutee data. Its HTTP status is an exercise artifact. "
      "Do not point external traffic at it or treat it as a deployment recipe."),
    p("Source references", "SectionGuide"),
    p("Backend health route: <b>myscoutee-backend/config/nginx/http/spring.conf</b>. "
      "Provider and forwarding semantics: <b>developer.hashicorp.com/vagrant/"
      "docs/providers</b> and <b>developer.hashicorp.com/vagrant/docs/networking/"
      "forwarded_ports</b>. Web consoles: <b>docs.ansible.com/ecosystem.html</b> "
      "and <b>help.puppet.com/pe/current/topics/complete_install_log_in.htm</b>.",
      "SmallGuide"),
    p("Terminal excerpts on pages 6-7 were observed through Vagrant QEMU/KVM "
      "on the optional local Ubuntu 24.04 box on 2026-10-28. The portable "
      "path targets Ubuntu 22.04; versions and change counts can differ.",
      "SmallGuide"),
]

if __name__ == "__main__":
    document = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, leftMargin=46, rightMargin=46,
        topMargin=106, bottomMargin=52,
        title="MyScoutee Infrastructure Configuration Lab Guide",
        author="MyScoutee / fssrepository",
    )
    document.build(story, onFirstPage=frame, onLaterPages=frame)
    print(OUTPUT)
