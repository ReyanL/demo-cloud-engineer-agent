"""Terraform command execution tools for infrastructure validation."""

import json
import logging
import os
import shutil
import subprocess
from typing import Optional

from strands import tool

# Configure the root strands logger
logging.getLogger("strands").setLevel(logging.INFO)
# Add a handler to see the logs
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


@tool
def terraform_init(project_path: str) -> str:
    """
    Initialize Terraform in the specified project directory.
    MUST succeed before terraform_plan can be run.

    Args:
        project_path: Path to the terraform project directory

    Returns:
        JSON string containing initialization result and any error messages
    """
    logger.info("Running terraform init in project path: %s", project_path)

    try:
        result = subprocess.run(
            ["terraform", "init"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            logger.info("Terraform init completed successfully in %s", project_path)
        else:
            logger.error(
                "Terraform init failed in %s with return code %d",
                project_path,
                result.returncode,
            )
            logger.error("Error output: %s", result.stderr)

        return json.dumps(
            {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": "terraform init",
            },
            indent=2,
        )
    except subprocess.TimeoutExpired:
        error_msg = "Terraform init timed out after 5 minutes"
        logger.error("%s in %s", error_msg, project_path)
        return json.dumps(
            {
                "success": False,
                "error": error_msg,
                "command": "terraform init",
            },
            indent=2,
        )
    except Exception as e:
        logger.exception(
            "Unexpected error during terraform init in %s: %s", project_path, str(e)
        )
        return json.dumps(
            {"success": False, "error": str(e), "command": "terraform init"},
            indent=2,
        )


@tool
def tflint(project_path: str) -> str:
    """
    Fix linting errors using tflint.
    Run after terraform_init to lint and auto-fix Terraform code.

    Args:
        project_path: Path to the terraform project directory

    Returns:
        JSON string containing tflint result and any error messages
    """
    logger.info("Running tflint with --fix in project path: %s", project_path)
    
    # Verify project path exists and contains tflint.hcl
    if not os.path.exists(project_path):
        error_msg = f"Project path does not exist: {project_path}"
        logger.error(error_msg)
        return json.dumps(
            {"success": False, "error": error_msg, "command": "tflint"},
            indent=2,
        )
    
    tflint_config_path = os.path.join(project_path, "tflint.hcl")
    if not os.path.exists(tflint_config_path):
        logger.warning("tflint.hcl not found at %s, tflint will use default configuration", tflint_config_path)
    else:
        logger.info("Found tflint.hcl configuration at %s", tflint_config_path)

    try:
        # Run tflint --init first to install plugins
        init_cmd = ["tflint", "--init"]
        logger.info("Running tflint --init to install plugins")
        init_result = subprocess.run(
            init_cmd, cwd=project_path, capture_output=True, text=True, timeout=300
        )

        if init_result.returncode != 0:
            logger.warning(
                "tflint --init had issues in %s with return code %d",
                project_path,
                init_result.returncode,
            )
            logger.warning("Init stdout: %s", init_result.stdout)
            logger.warning("Init stderr: %s", init_result.stderr)

        # Now run tflint --fix
        cmd = ["tflint", "--fix"]
        logger.info("Running tflint --fix command: %s", " ".join(cmd))

        result = subprocess.run(
            cmd, cwd=project_path, capture_output=True, text=True, timeout=300
        )

        if result.returncode == 0:
            logger.info("tflint completed successfully in %s", project_path)
        else:
            logger.error(
                "tflint failed in %s with return code %d",
                project_path,
                result.returncode,
            )
            logger.error("tflint stdout: %s", result.stdout)
            logger.error("tflint stderr: %s", result.stderr)
            
        # Include both init and main command results in response
        combined_stdout = f"=== tflint --init output ===\n{init_result.stdout}\n\n=== tflint --fix output ===\n{result.stdout}"
        combined_stderr = f"=== tflint --init errors ===\n{init_result.stderr}\n\n=== tflint --fix errors ===\n{result.stderr}"

        return json.dumps(
            {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": combined_stdout,
                "stderr": combined_stderr,
                "command": " ".join(cmd),
                "init_success": init_result.returncode == 0,
                "init_returncode": init_result.returncode,
            },
            indent=2,
        )
    except subprocess.TimeoutExpired:
        error_msg = "tflint timed out after 5 minutes"
        logger.error("%s in %s", error_msg, project_path)
        return json.dumps(
            {
                "success": False,
                "error": error_msg,
                "command": " ".join(cmd),
            },
            indent=2,
        )
    except Exception as e:
        logger.exception(
            "Unexpected error during tflint in %s: %s", project_path, str(e)
        )
        return json.dumps(
            {"success": False, "error": str(e), "command": " ".join(cmd)}, indent=2
        )


@tool
def terraform_validate(project_path: str) -> str:
    """
    Validate Terraform configuration files in the specified project directory.
    Requires terraform_init to be run successfully first.
    MUST succeed before terraform_plan can be run.

    Args:
        project_path: Path to the terraform project directory

    Returns:
        JSON string containing validation result and any error messages
    """
    logger.info("Running terraform validate in project path: %s", project_path)

    try:
        result = subprocess.run(
            ["terraform", "validate"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            logger.info("Terraform validate completed successfully in %s", project_path)
        else:
            logger.error(
                "Terraform validate failed in %s with return code %d",
                project_path,
                result.returncode,
            )
            logger.error("Error output: %s", result.stderr)

        return json.dumps(
            {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": "terraform validate",
            },
            indent=2,
        )
    except subprocess.TimeoutExpired:
        error_msg = "Terraform validate timed out after 1 minute"
        logger.error("%s in %s", error_msg, project_path)
        return json.dumps(
            {
                "success": False,
                "error": error_msg,
                "command": "terraform validate",
            },
            indent=2,
        )
    except Exception as e:
        logger.exception(
            "Unexpected error during terraform validate in %s: %s", project_path, str(e)
        )
        return json.dumps(
            {"success": False, "error": str(e), "command": "terraform validate"},
            indent=2,
        )


@tool
def terraform_plan(project_path: str, var_file: Optional[str] = None) -> str:
    """
    Generate Terraform execution plan.
    Requires terraform_init to be run successfully first.
    This is the verification step to ensure the Terraform configuration is correct.

    Args:
        project_path: Path to the terraform project directory
        var_file: Optional path to variables file

    Returns:
        JSON string containing plan result and any error messages
    """
    logger.info("Running terraform plan in project path: %s", project_path)
    if var_file:
        logger.info("Using var file: %s", var_file)

    try:
        cmd = ["terraform", "plan", "-no-color"]
        if var_file:
            cmd.extend(["-var-file", var_file])

        result = subprocess.run(
            cmd, cwd=project_path, capture_output=True, text=True, timeout=300
        )

        if result.returncode == 0:
            logger.info("Terraform plan completed successfully in %s", project_path)
        else:
            logger.error(
                "Terraform plan failed in %s with return code %d",
                project_path,
                result.returncode,
            )
            logger.error("Error output: %s", result.stderr)

        return json.dumps(
            {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd),
            },
            indent=2,
        )
    except subprocess.TimeoutExpired:
        error_msg = "Terraform plan timed out after 5 minutes"
        logger.error("%s in %s", error_msg, project_path)
        return json.dumps(
            {
                "success": False,
                "error": error_msg,
                "command": " ".join(cmd),
            },
            indent=2,
        )
    except Exception as e:
        logger.exception(
            "Unexpected error during terraform plan in %s: %s", project_path, str(e)
        )
        return json.dumps(
            {"success": False, "error": str(e), "command": " ".join(cmd)}, indent=2
        )
