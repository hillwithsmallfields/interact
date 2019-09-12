#!/usr/bin/env python3

import sys

def main():
    print("""Use of the Oracle network and applications is intended solely for Oracle's authorized users. The use of these resources by Oracle employees and contractors is subject to company policies, including the Code of Conduct, Acceptable Use Policy and Information Protection Policy; access may be monitored and logged, to the extent permitted by law, in accordance with Oracle policies. Unauthorized access or use may result in termination of your access, disciplinary action and/or civil and criminal penalties. Further information about Oracle security and privacy policies is available at the GIS Policy Portal.
GROUP: [odc-admin|odc-dh|odc-mfa-admin|odc-mfa-user|odc-test|odc-user|safenet]:\n\n""")
    a1 = sys.stdin.readline()
    print("Got", a1)

if __name__ == "__main__":
    sys.exit(main())
