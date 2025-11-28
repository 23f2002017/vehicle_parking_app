export default {
    template : `
        <div style="padding-bottom: 20px;">
            <p v-if='message != ""' style="color: red">{{message}}</p>
            <div v-else>
                <h2>Users</h2>
                <table style="border: 2px solid black; width: 80%">
                    <tr style="text-align: center; border: 1px solid black; padding: 4px;">
                        <th style="text-align: center; border: 1px solid black; padding: 8px;">User ID</th>
                        <th style="text-align: center; border: 1px solid black; padding: 8px;">Name</th>
                        <th style="text-align: center; border: 1px solid black; padding: 8px;">E-Mail</th>
                        <th style="text-align: center; border: 1px solid black; padding: 8px;">Total Parkings</th>
                        <th style="text-align: center; border: 1px solid black; padding: 8px;">Actions</th>
                    </tr>
                    <tr v-for="user in users" style="text-align: center; border: 2px solid black; padding: 4px;">
                        <td style="text-align: center; border: 1px solid black; padding: 8px;">{{user.id}}</td>
                        <td style="text-align: center; border: 1px solid black; padding: 8px;">{{user.name}}</td>
                        <td style="text-align: center; border: 1px solid black; padding: 8px;">{{user.email}}</td>
                        <td style="text-align: center; border: 1px solid black; padding: 8px;">{{user.total_parkings}}</td>
                        <td v-if="user.is_active" style="text-align: center; border: 1px solid black; padding: 8px;"><button @click="() => ChangeStatus(user.id)">Block</button></td>
                        <td v-else style="text-align: center; border: 1px solid black; padding: 8px;"><button @click="() => ChangeStatus(user.id)">Unblock</button></td>
                    </tr>
                </table>
            </div>   
        </div>
     `,
    data() {
        return {
            message : "",
            users : []
        }
    },
    methods : {
        ChangeStatus: function(id) {
            fetch(`/api/users/change_status/${id}`, {
                method: "PUT",
                headers: {
                    "auth-token": localStorage.getItem("auth_token")
                }
            }).then(res => res.json()).then(data => {
                alert(data.message) 
                this.LoadUser()   
            })
        },
        LoadUser: async function() {
            const res = await fetch("/api/users", {
            method: "GET",
            headers: {
                "auth-token" : localStorage.getItem("auth_token")
            }
            })
            const data = await res.json()
            if (res.ok) {
                this.users = data.user_list
            } else {
                this.message = data.message
            }
        }    
    },
    mounted() {
        this.LoadUser()
    }
}