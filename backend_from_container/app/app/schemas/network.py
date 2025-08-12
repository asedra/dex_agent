"""Network configuration schemas."""
from pydantic import BaseModel, Field, IPvAnyAddress
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class NetworkAdapterStatus(str, Enum):
    """Network adapter status."""
    UP = "up"
    DOWN = "down"
    DISCONNECTED = "disconnected"
    DISABLED = "disabled"
    UNKNOWN = "unknown"


class NetworkAdapterType(str, Enum):
    """Network adapter type."""
    ETHERNET = "ethernet"
    WIFI = "wifi"
    BLUETOOTH = "bluetooth"
    VPN = "vpn"
    VIRTUAL = "virtual"
    LOOPBACK = "loopback"
    OTHER = "other"


class IPConfiguration(BaseModel):
    """IP configuration details."""
    address: str = Field(..., description="IP address")
    subnet_mask: str = Field(..., description="Subnet mask")
    prefix_length: int = Field(..., description="Prefix length")
    is_dhcp: bool = Field(..., description="Is DHCP assigned")


class DNSConfiguration(BaseModel):
    """DNS configuration."""
    servers: List[str] = Field(..., description="DNS server addresses")
    suffix: Optional[str] = Field(None, description="DNS suffix")
    search_domains: List[str] = Field(default_factory=list, description="Search domains")


class NetworkAdapter(BaseModel):
    """Network adapter information."""
    id: str = Field(..., description="Adapter ID")
    name: str = Field(..., description="Adapter name")
    description: str = Field(..., description="Adapter description")
    type: NetworkAdapterType = Field(..., description="Adapter type")
    status: NetworkAdapterStatus = Field(..., description="Adapter status")
    mac_address: Optional[str] = Field(None, description="MAC address")
    speed_mbps: Optional[int] = Field(None, description="Link speed in Mbps")
    ipv4_addresses: List[IPConfiguration] = Field(default_factory=list)
    ipv6_addresses: List[IPConfiguration] = Field(default_factory=list)
    gateway: Optional[str] = Field(None, description="Default gateway")
    dns: DNSConfiguration = Field(..., description="DNS configuration")
    dhcp_enabled: bool = Field(..., description="DHCP enabled")
    dhcp_server: Optional[str] = Field(None, description="DHCP server address")
    bytes_sent: int = Field(0, description="Total bytes sent")
    bytes_received: int = Field(0, description="Total bytes received")
    packets_sent: int = Field(0, description="Total packets sent")
    packets_received: int = Field(0, description="Total packets received")
    errors_in: int = Field(0, description="Input errors")
    errors_out: int = Field(0, description="Output errors")


class NetworkAdapterListResponse(BaseModel):
    """Response for network adapter list."""
    adapters: List[NetworkAdapter]
    total: int
    timestamp: datetime


class NetworkConfigRequest(BaseModel):
    """Request to configure network adapter."""
    adapter_id: str = Field(..., description="Adapter ID")
    ip_address: Optional[str] = Field(None, description="Static IP address")
    subnet_mask: Optional[str] = Field(None, description="Subnet mask")
    gateway: Optional[str] = Field(None, description="Default gateway")
    dns_servers: Optional[List[str]] = Field(None, description="DNS servers")
    dhcp_enabled: Optional[bool] = Field(None, description="Enable DHCP")


class NetworkConfigResponse(BaseModel):
    """Response for network configuration."""
    success: bool
    message: str
    adapter: Optional[NetworkAdapter] = None


class NetworkTestRequest(BaseModel):
    """Request for network connectivity test."""
    target: str = Field(..., description="Target host or IP")
    test_type: str = Field("ping", description="Test type: ping, traceroute, nslookup")
    count: int = Field(4, description="Number of packets/attempts")
    timeout: int = Field(5, description="Timeout in seconds")


class NetworkTestResponse(BaseModel):
    """Response for network test."""
    success: bool
    test_type: str
    target: str
    results: Dict[str, Any]
    timestamp: datetime


class FirewallRule(BaseModel):
    """Firewall rule configuration."""
    name: str = Field(..., description="Rule name")
    enabled: bool = Field(..., description="Rule enabled")
    direction: str = Field(..., description="inbound or outbound")
    action: str = Field(..., description="allow or block")
    protocol: Optional[str] = Field(None, description="Protocol: TCP, UDP, Any")
    local_port: Optional[str] = Field(None, description="Local port or range")
    remote_port: Optional[str] = Field(None, description="Remote port or range")
    local_address: Optional[str] = Field(None, description="Local IP or range")
    remote_address: Optional[str] = Field(None, description="Remote IP or range")
    program: Optional[str] = Field(None, description="Program path")
    profile: Optional[str] = Field(None, description="Profile: Domain, Private, Public")


class FirewallRulesResponse(BaseModel):
    """Response for firewall rules list."""
    rules: List[FirewallRule]
    total: int
    profiles: Dict[str, bool]  # Profile status (enabled/disabled)


class RouteEntry(BaseModel):
    """Network route entry."""
    destination: str = Field(..., description="Destination network")
    mask: str = Field(..., description="Network mask")
    gateway: str = Field(..., description="Gateway address")
    interface: str = Field(..., description="Interface")
    metric: int = Field(..., description="Route metric")
    persistent: bool = Field(..., description="Is persistent route")


class RoutingTableResponse(BaseModel):
    """Response for routing table."""
    routes: List[RouteEntry]
    total: int


class NetworkShareInfo(BaseModel):
    """Network share information."""
    name: str = Field(..., description="Share name")
    path: str = Field(..., description="Local path")
    description: Optional[str] = Field(None, description="Share description")
    type: str = Field(..., description="Share type")
    permissions: Optional[str] = Field(None, description="Permissions")
    max_users: Optional[int] = Field(None, description="Maximum users")
    current_users: int = Field(0, description="Current users")


class NetworkSharesResponse(BaseModel):
    """Response for network shares."""
    shares: List[NetworkShareInfo]
    total: int


class VPNConnection(BaseModel):
    """VPN connection information."""
    name: str = Field(..., description="Connection name")
    type: str = Field(..., description="VPN type")
    status: str = Field(..., description="Connection status")
    server: str = Field(..., description="VPN server")
    username: Optional[str] = Field(None, description="Username")
    connected_time: Optional[datetime] = Field(None, description="Connection time")
    bytes_sent: int = Field(0, description="Bytes sent")
    bytes_received: int = Field(0, description="Bytes received")


class VPNConnectionsResponse(BaseModel):
    """Response for VPN connections."""
    connections: List[VPNConnection]
    total: int