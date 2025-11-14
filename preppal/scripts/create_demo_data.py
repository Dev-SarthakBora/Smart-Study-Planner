"""
Create Demo Study Materials for PrepPal
Generates a sample PDF for immediate testing
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

def create_demo_pdf():
    """Create a sample computer networks study material PDF"""
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Create PDF
    filename = 'data/demo.pdf'
    doc = SimpleDocTemplate(filename, pagesize=letter)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='darkblue',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='darkgreen',
        spaceAfter=12,
        spaceBefore=12
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=12,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    # Title
    title = Paragraph("Computer Networks End Semester Notes", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Introduction
    intro = Paragraph(
        "These comprehensive notes cover fundamental concepts in computer networks and data communication. "
        "Topics include network architectures, protocols, and emerging technologies.",
        body_style
    )
    elements.append(intro)
    elements.append(Spacer(1, 0.2*inch))
    
    # Chapter 1: Network Fundamentals
    heading1 = Paragraph("Chapter 1: Network Fundamentals", heading_style)
    elements.append(heading1)
    
    content1 = [
        "A computer network is a collection of interconnected devices that can communicate and share resources. "
        "Networks are classified by their geographical scope: Local Area Networks (LANs) cover small areas like "
        "buildings, Metropolitan Area Networks (MANs) span cities, and Wide Area Networks (WANs) connect across "
        "countries or continents.",
        
        "The OSI (Open Systems Interconnection) model defines seven layers of network communication: Physical, "
        "Data Link, Network, Transport, Session, Presentation, and Application. Each layer has specific "
        "responsibilities and communicates with adjacent layers.",
        
        "Network topologies describe how devices are arranged. Common topologies include bus (all devices on "
        "a single cable), star (all devices connected to a central hub), ring (devices in a circular configuration), "
        "and mesh (multiple interconnections between devices)."
    ]
    
    for para in content1:
        elements.append(Paragraph(para, body_style))
        elements.append(Spacer(1, 0.15*inch))
    
    # Chapter 2: Transmission Media
    heading2 = Paragraph("Chapter 2: Transmission Media", heading_style)
    elements.append(heading2)
    
    content2 = [
        "Transmission media are the physical pathways that connect devices in a network. They are classified "
        "into two main categories: guided media (wired) and unguided media (wireless).",
        
        "Guided media include twisted pair cables (used in Ethernet), coaxial cables (cable TV and internet), "
        "and fiber optic cables (high-speed data transmission using light). Fiber optics offer the highest "
        "bandwidth and are immune to electromagnetic interference.",
        
        "Unguided media use electromagnetic waves transmitted through air or vacuum. Examples include radio "
        "waves (Wi-Fi, cellular), microwaves (satellite communication), and infrared (remote controls, short-range "
        "data transfer)."
    ]
    
    for para in content2:
        elements.append(Paragraph(para, body_style))
        elements.append(Spacer(1, 0.15*inch))
    
    elements.append(PageBreak())
    
    # Chapter 3: Network Protocols
    heading3 = Paragraph("Chapter 3: Network Protocols", heading_style)
    elements.append(heading3)
    
    content3 = [
        "Network protocols are standardized rules that govern how data is transmitted across networks. The TCP/IP "
        "protocol suite is the foundation of modern internet communication.",
        
        "The Internet Protocol (IP) handles addressing and routing of data packets. IPv4 uses 32-bit addresses, "
        "while IPv6 uses 128-bit addresses to accommodate the growing number of internet devices. IP is a "
        "connectionless protocol that does not guarantee delivery.",
        
        "The Transmission Control Protocol (TCP) provides reliable, ordered delivery of data. It establishes "
        "connections, manages flow control, and ensures error-free transmission through acknowledgments and "
        "retransmissions. HTTP, FTP, and SMTP all use TCP.",
        
        "User Datagram Protocol (UDP) is a simpler, connectionless protocol that prioritizes speed over reliability. "
        "It's used for applications like video streaming, online gaming, and DNS queries where occasional packet "
        "loss is acceptable."
    ]
    
    for para in content3:
        elements.append(Paragraph(para, body_style))
        elements.append(Spacer(1, 0.15*inch))
    
    # Chapter 4: Network Security
    heading4 = Paragraph("Chapter 4: Network Security", heading_style)
    elements.append(heading4)
    
    content4 = [
        "Network security protects data during transmission and storage. Key concepts include confidentiality "
        "(keeping data private), integrity (ensuring data hasn't been altered), and availability (ensuring "
        "resources are accessible).",
        
        "Cryptography uses mathematical algorithms to encrypt data. Symmetric encryption uses the same key for "
        "encryption and decryption (e.g., AES), while asymmetric encryption uses public-private key pairs (e.g., RSA). "
        "Digital signatures ensure authenticity and non-repudiation.",
        
        "Firewalls monitor and control network traffic based on security rules. They can be hardware devices or "
        "software applications. Modern firewalls include features like intrusion detection, malware scanning, "
        "and VPN support.",
        
        "Virtual Private Networks (VPNs) create secure, encrypted tunnels over public networks. They're used "
        "for remote access, site-to-site connections, and protecting privacy. VPNs implement protocols like "
        "IPsec, SSL/TLS, and WireGuard."
    ]
    
    for para in content4:
        elements.append(Paragraph(para, body_style))
        elements.append(Spacer(1, 0.15*inch))
    
    elements.append(PageBreak())
    
    # Chapter 5: Wireless Networks
    heading5 = Paragraph("Chapter 5: Wireless Networks", heading_style)
    elements.append(heading5)
    
    content5 = [
        "Wireless networks use radio frequency signals to connect devices without physical cables. Wi-Fi (IEEE 802.11) "
        "is the most common wireless LAN technology, operating in the 2.4 GHz and 5 GHz frequency bands.",
        
        "Wi-Fi standards have evolved significantly: 802.11b (11 Mbps), 802.11g (54 Mbps), 802.11n (600 Mbps), "
        "802.11ac (several Gbps), and the latest 802.11ax (Wi-Fi 6) offering improved performance in congested "
        "environments.",
        
        "Cellular networks provide wide-area wireless connectivity for mobile devices. Technologies have progressed "
        "from 1G (analog voice) to 5G (high-speed data, low latency, massive device connectivity). 5G enables "
        "applications like autonomous vehicles and smart cities.",
        
        "Bluetooth is a short-range wireless technology for personal area networks (PANs). It's used for connecting "
        "peripherals, audio devices, and IoT sensors. Bluetooth Low Energy (BLE) enables long battery life for "
        "wearables and sensors."
    ]
    
    for para in content5:
        elements.append(Paragraph(para, body_style))
        elements.append(Spacer(1, 0.15*inch))
    
    # Summary
    summary_heading = Paragraph("Summary and Key Takeaways", heading_style)
    elements.append(summary_heading)
    
    summary = Paragraph(
        "Computer networks form the backbone of modern communication and information systems. Understanding network "
        "fundamentals, protocols, security, and wireless technologies is essential for IT professionals. As networks "
        "continue to evolve with technologies like 5G, IoT, and edge computing, staying current with networking "
        "concepts remains crucial for career success.",
        body_style
    )
    elements.append(summary)
    
    # Build PDF
    doc.build(elements)
    print(f"✅ Demo PDF created successfully: {filename}")
    print(f"📄 File size: {os.path.getsize(filename) / 1024:.2f} KB")
    return filename

if __name__ == "__main__":
    print("Creating demo study material...")
    try:
        filename = create_demo_pdf()
        print("\n🎉 Demo data creation complete!")
        print(f"You can now upload {filename} in PrepPal to test the system.")
    except ImportError:
        print("\n⚠️  reportlab not installed. Creating text file instead...")
        # Fallback: create a text file
        os.makedirs('data', exist_ok=True)
        with open('data/demo_notes.txt', 'w') as f:
            f.write("""Computer Networks End Semester Notes

Chapter 1: Network Fundamentals

A computer network is a collection of interconnected devices that can communicate and share resources. Networks are classified by their geographical scope: Local Area Networks (LANs) cover small areas like buildings, Metropolitan Area Networks (MANs) span cities, and Wide Area Networks (WANs) connect across countries or continents.

The OSI model defines seven layers of network communication: Physical, Data Link, Network, Transport, Session, Presentation, and Application. Each layer has specific responsibilities and communicates with adjacent layers.

Chapter 2: Transmission Media

Transmission media are the physical pathways that connect devices in a network. Guided media include twisted pair cables, coaxial cables, and fiber optic cables. Unguided media use electromagnetic waves transmitted through air or vacuum.

Chapter 3: Network Protocols

Network protocols are standardized rules that govern data transmission. TCP/IP is the foundation of modern internet communication. IP handles addressing and routing, while TCP provides reliable delivery. UDP offers faster but less reliable transmission.

Chapter 4: Network Security

Network security protects data during transmission and storage through cryptography, firewalls, and VPNs. Key concepts include confidentiality, integrity, and availability.

Chapter 5: Wireless Networks

Wireless networks use radio frequency signals. Wi-Fi is the most common wireless LAN technology. Cellular networks provide wide-area connectivity. Bluetooth enables short-range personal area networks.
""")
        print("✅ Text file created: data/demo_notes.txt")
        print("📝 For PDF creation, install reportlab: pip install reportlab")