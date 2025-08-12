"""Software management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import List, Optional, Dict, Any
import json

from app.core.auth import get_current_user
from app.schemas.software import (
    SoftwarePackageCreate,
    SoftwarePackageUpdate,
    SoftwarePackageResponse,
    InstalledSoftwareResponse,
    InstallationJobCreate,
    InstallationJobUpdate,
    InstallationJobResponse,
    SoftwareInventoryRequest,
    SoftwareInstallRequest,
    SoftwareUninstallRequest,
    PackageUploadResponse,
    SoftwareRepositoryCreate,
    SoftwareRepositoryResponse,
    BulkInstallRequest,
    InstallationProgressUpdate
)
from app.services.software_service import SoftwareService
from app.models.software import PackageType

router = APIRouter(prefix="/software")
software_service = SoftwareService()


@router.get("/packages", response_model=List[SoftwarePackageResponse])
async def list_packages(
    category: Optional[str] = None,
    package_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all available software packages."""
    try:
        # TODO: Implement database query
        packages = []
        return packages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/packages", response_model=SoftwarePackageResponse)
async def create_package(
    package: SoftwarePackageCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new software package entry."""
    try:
        # TODO: Implement package creation
        return SoftwarePackageResponse(
            id=1,
            **package.dict(),
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/packages/{package_id}", response_model=SoftwarePackageResponse)
async def get_package(
    package_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific software package."""
    try:
        package = await software_service._get_package(package_id)
        if not package:
            raise HTTPException(status_code=404, detail="Package not found")
        return package
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/packages/{package_id}", response_model=SoftwarePackageResponse)
async def update_package(
    package_id: int,
    package: SoftwarePackageUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a software package."""
    try:
        # TODO: Implement package update
        return SoftwarePackageResponse(
            id=package_id,
            name="Updated Package",
            version="1.0.0",
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/packages/{package_id}")
async def delete_package(
    package_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a software package."""
    try:
        # TODO: Implement package deletion
        return {"message": "Package deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/packages/upload", response_model=PackageUploadResponse)
async def upload_package(
    file: UploadFile = File(...),
    name: str = Form(...),
    version: str = Form(...),
    description: Optional[str] = Form(None),
    package_type: str = Form("exe"),
    vendor: Optional[str] = Form(None),
    silent_install_args: Optional[str] = Form(None),
    silent_uninstall_args: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Upload a software package file."""
    try:
        # Read file content
        file_content = await file.read()
        
        # Prepare package info
        package_info = {
            "name": name,
            "version": version,
            "description": description,
            "package_type": package_type,
            "vendor": vendor,
            "silent_install_args": silent_install_args,
            "silent_uninstall_args": silent_uninstall_args
        }
        
        # Upload package
        result = await software_service.upload_package(
            file_content=file_content,
            filename=file.filename,
            package_info=package_info
        )
        
        if result.get('success'):
            return PackageUploadResponse(
                package_id=result['package_id'],
                filename=result['filename'],
                size_bytes=result['size_bytes'],
                checksum=result['checksum'],
                upload_path=result['upload_path']
            )
        else:
            raise HTTPException(status_code=500, detail=result.get('error'))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}/installed", response_model=List[InstalledSoftwareResponse])
async def get_installed_software(
    agent_id: str,
    refresh: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get installed software list from an agent."""
    try:
        software_list = await software_service.get_installed_software(agent_id, refresh)
        
        # Convert to response model
        response_list = []
        for idx, software in enumerate(software_list):
            response_list.append(InstalledSoftwareResponse(
                id=idx + 1,
                agent_id=agent_id,
                name=software.get('Name', 'Unknown'),
                version=software.get('Version', ''),
                vendor=software.get('Vendor'),
                install_location=software.get('InstallLocation'),
                uninstall_string=software.get('UninstallString'),
                registry_key=software.get('RegistryKey'),
                size_bytes=software.get('EstimatedSize'),
                detected_at="2024-01-01T00:00:00"
            ))
        
        return response_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_id}/install")
async def install_software(
    agent_id: str,
    request: SoftwareInstallRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Install software on an agent."""
    try:
        # Start installation in background
        background_tasks.add_task(
            software_service.install_software,
            agent_id=agent_id,
            package_id=request.package_id,
            package_name=request.package_name,
            package_type=request.package_type,
            version=request.version,
            silent=request.silent,
            custom_args=request.custom_args,
            install_script=request.install_script
        )
        
        return {
            "message": "Installation started",
            "agent_id": agent_id,
            "package_name": request.package_name or f"Package {request.package_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_id}/uninstall")
async def uninstall_software(
    agent_id: str,
    request: SoftwareUninstallRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Uninstall software from an agent."""
    try:
        # Start uninstallation in background
        background_tasks.add_task(
            software_service.uninstall_software,
            agent_id=agent_id,
            software_id=request.software_id,
            software_name=request.software_name,
            silent=request.silent,
            custom_args=request.custom_args
        )
        
        return {
            "message": "Uninstallation started",
            "agent_id": agent_id,
            "software": request.software_name or f"Software {request.software_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs", response_model=List[InstallationJobResponse])
async def list_installation_jobs(
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List installation jobs."""
    try:
        # TODO: Implement job listing
        jobs = []
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}", response_model=InstallationJobResponse)
async def get_installation_job(
    job_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get installation job details."""
    try:
        # TODO: Implement job retrieval
        return InstallationJobResponse(
            id=job_id,
            agent_id="agent-1",
            package_id=1,
            status="pending",
            progress_percent=0,
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/jobs/{job_id}/cancel")
async def cancel_installation_job(
    job_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Cancel an installation job."""
    try:
        # TODO: Implement job cancellation
        return {"message": f"Job {job_id} cancelled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-install")
async def bulk_install(
    request: BulkInstallRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Install software on multiple agents."""
    try:
        jobs = []
        
        for agent_id in request.agent_ids:
            for package_id in request.package_ids:
                # Start installation for each agent-package combination
                background_tasks.add_task(
                    software_service.install_software,
                    agent_id=agent_id,
                    package_id=package_id,
                    silent=True
                )
                jobs.append({
                    "agent_id": agent_id,
                    "package_id": package_id
                })
        
        return {
            "message": f"Started {len(jobs)} installation jobs",
            "jobs": jobs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repositories", response_model=List[SoftwareRepositoryResponse])
async def list_repositories(
    current_user: dict = Depends(get_current_user)
):
    """List software repositories."""
    try:
        # TODO: Implement repository listing
        repositories = [
            SoftwareRepositoryResponse(
                id=1,
                name="Chocolatey",
                type="chocolatey",
                url="https://community.chocolatey.org/api/v2/",
                enabled=True,
                priority=0,
                created_at="2024-01-01T00:00:00",
                updated_at="2024-01-01T00:00:00"
            ),
            SoftwareRepositoryResponse(
                id=2,
                name="Windows Package Manager",
                type="winget",
                enabled=True,
                priority=1,
                created_at="2024-01-01T00:00:00",
                updated_at="2024-01-01T00:00:00"
            )
        ]
        return repositories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repositories", response_model=SoftwareRepositoryResponse)
async def create_repository(
    repository: SoftwareRepositoryCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a software repository."""
    try:
        # TODO: Implement repository creation
        return SoftwareRepositoryResponse(
            id=1,
            **repository.dict(),
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chocolatey/search")
async def search_chocolatey(
    query: str,
    current_user: dict = Depends(get_current_user)
):
    """Search Chocolatey packages."""
    try:
        # TODO: Implement Chocolatey search
        return {
            "packages": [
                {
                    "name": "googlechrome",
                    "version": "120.0.0",
                    "description": "Google Chrome Browser"
                },
                {
                    "name": "firefox",
                    "version": "121.0",
                    "description": "Mozilla Firefox"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/winget/search")
async def search_winget(
    query: str,
    current_user: dict = Depends(get_current_user)
):
    """Search Windows Package Manager packages."""
    try:
        # TODO: Implement winget search
        return {
            "packages": [
                {
                    "id": "Microsoft.VisualStudioCode",
                    "name": "Visual Studio Code",
                    "version": "1.85.0",
                    "publisher": "Microsoft Corporation"
                },
                {
                    "id": "Git.Git",
                    "name": "Git",
                    "version": "2.43.0",
                    "publisher": "Git for Windows"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))