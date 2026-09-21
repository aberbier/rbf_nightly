*** Variables ***

${CREATE_USER}              /api/v1/users
${GET_USER}                 /api/v1/users/{}
${DELETE_USER}              /api/v1/users/{}

${GET_USER_ROLES}           /api/v1/users/{}/roles/{}
${CREATE_ROLE}              /api/v1/roles
${DELETE_ROLE}              /api/v1/roles/{}

${LOGIN}                    /api/v1/login