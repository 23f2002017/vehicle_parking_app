export default {
    template : `
        <div style="margin: 20px">
            <h1>Adding a Parking Lot</h1>
            <p style="color: red">{{message}}</p>
            <form @submit.prevent="AddLot">
                <fieldset style="margin-right: 940px;">
                    <legend>Input Parking Lot Details</legend>
                        <p>Lot Name : <input type="text" v-model="LotDetails.name"></p>
                        <p>Address : <textarea type="text" v-model="LotDetails.address"/></p>
                        <p>Pincode : <input type="text" v-model="LotDetails.pincode"/></p>
                        <p>No of Spots : <input type="number" v-model="LotDetails.no_of_spots"/></p>
                        <p>Price/hr : <input type="number" v-model="LotDetails.price"/></p>    
                        <button type="submit"> Add </button>
                </fieldset>
            </form>    
        </div>    
    `,
    data() {
        return {
            LotDetails : {
                name :  "",
                address :  "",
                pincode :  "",
                no_of_spots : null,
                price : null
            },
            message : ""
        }
    },
    methods : {
        AddLot: async function() {
            const payload = {
                ...this.LotDetails,
                no_of_spots : parseInt(this.LotDetails.no_of_spots, 10),
                price : parseFloat(this.LotDetails.price)
            }
            const response = await fetch("/api/parking_lot", {
                    method : "POST",
                    headers : {
                        "Content-Type": "application/json",
                        "auth-token" : localStorage.getItem("auth_token")
                    },
                    body : JSON.stringify(payload)
                })
            const data = await response.json()
            if (response.ok) {
                this.$router.push("/admin_dashboard/parking_lots")
            } else {
                this.message = data.message;
            }
        }
    }
}