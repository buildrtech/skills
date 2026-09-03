# Request

From: VP of Operations, Millbrook Builders (synthetic)
Date: February 16, 2027

Give me the Q1 forecast for work in progress and tell me which projects
moved margin more than two points since the last close.

Context the agent should discover, not assume (synthetic account state):

- Buildr MCP server is connected with read and write scopes.
- The `wip` tab holds four projects: prj_1001 Harbor Street Parking
  Structure, prj_1002 Cedar Ridge Middle School Renovation, prj_1003
  Northgate Distribution Center, prj_1004 Riverside Clinic Tenant
  Improvement.
- All four projects have closed periods through January 2027. December 2026
  is the close before that. February and March 2027 are forecast periods.
- No change orders were approved between the December and January closes on
  any of the four projects. Harbor Street has one approved change order of
  $400,000 dated October 2026, already in its contract value.
