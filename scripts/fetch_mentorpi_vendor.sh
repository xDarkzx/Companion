#!/usr/bin/env bash
# Fetch MentorPi driver packages into ros2_ws/src/vendor (Jazzy-compatible set).
# Official Hiwonder image still requires order email — this uses the community port.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR="${ROOT}/ros2_ws/src/vendor"
TMP="$(mktemp -d)"
REPO="https://github.com/LinusGro/MentorPi_ris.git"

PACKAGES=(
  calibration
  imu_calib
  ldrobot-lidar-ros2
  peripherals
  driver
  orchestrator_launch
  simulations
)

echo ">>> clone MentorPi_ris (drivers only)"
git clone --depth 1 "${REPO}" "${TMP}/MentorPi_ris"

mkdir -p "${VENDOR}"
for pkg in "${PACKAGES[@]}"; do
  src="${TMP}/MentorPi_ris/ros2_ws/src/${pkg}"
  dst="${VENDOR}/${pkg}"
  if [[ ! -d "${src}" ]]; then
    echo "WARN: missing package ${pkg} in upstream repo"
    continue
  fi
  rm -rf "${dst}"
  cp -a "${src}" "${dst}"
  echo "    installed ${pkg}"
done

rm -f "${VENDOR}/COLCON_IGNORE" 2>/dev/null || true
rm -rf "${TMP}"

echo ">>> done — vendor packages in ${VENDOR}"
echo ">>> next: cd ros2_ws && rosdep install --from-paths src --ignore-src -r -y && colcon build"
