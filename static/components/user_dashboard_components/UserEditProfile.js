export default {
    template : `
        <div style="margin: 20px; height:65vh">
            <h2>Update Profile Page</h2>
            <p style="color: red">{{message}}</p>
            <form @submit.prevent="UpdateProfile">
                <fieldset style="margin-right: 920px;">
                    <legend>Update Profile</legend>
                        <p>Name : <input type="text" v-model="ProfileData.name" style="width:71%;" required/></p>
                        <p>Email : <input type="email" v-model="ProfileData.email" style="width:72%;" required/></p>
                        <p>Password : <input type="password" v-model="ProfileData.password" style="width:60%;" required/></p>
                        <button type="submit"> Update </button>
                </fieldset>
            </form> 
            <p style="color: red; font-size: small" >Note : Type the existing password if you don't want to change it</p>    
        </div>
    `,
    data() {
        return {
            ProfileData : {
                name :  "",
                email :  "",
                password :  ""
            },
            message : ""
        }
    },
    methods : {
        UpdateProfile: async function() {
            const res = await fetch("/api/profile", {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "auth-token" : localStorage.getItem("auth_token")
                },
                body: JSON.stringify(this.ProfileData)
            })
            const data = await res.json()
            if (res.ok) {
                alert(data.message)
                this.$router.push("/user_dashboard/home")
                window.location.reload()
            } else {
                this.message = data.message
            }
        }
    },
    mounted: async function() {
        const res = await fetch("/api/profile", {
            method: "GET",
            headers: {
                "auth-token" : localStorage.getItem("auth_token")
            }
        })
        const data = await res.json()
        if (res.ok) {
            this.ProfileData.name = data.user_profile.name 
            this.ProfileData.email = data.user_profile.email 
        } else {
            this.message = data.message
        }
    }
}
