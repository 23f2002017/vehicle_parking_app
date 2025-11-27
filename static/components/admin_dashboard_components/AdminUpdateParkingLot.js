export default {
    template : `
        <div style="margin: 20px">
            <h2>Updating Parking Lot {{this.$route.params.id}}</h2>
            <p style="color: red">{{message}}</p>
            <form @submit.prevent="UpdateLot">
                <fieldset style="margin-right: 920px;">
                    <legend>Update Parking Lot Details</legend>
                        <p>Lot Name : <input type="text" v-model="LotDetails.name"></p>
                        <p>Address : <textarea type="text" v-model="LotDetails.address"/></p>
                        <p>Pincode : <input type="text" v-model="LotDetails.pincode"/></p>
                        <p>No of Spots : <input type="number" v-model="LotDetails.no_of_spots"/></p>
                        <p>Price : <input type="number" v-model="LotDetails.price"/></p>    
                        <button type="submit"> Save </button>
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
    methods: {
        UpdateLot: async function() {
            const payload = {
                ...this.LotDetails,
                no_of_spots : parseInt(this.LotDetails.no_of_spots, 10),
                price : parseFloat(this.LotDetails.price)
            }
            const response = await fetch(`/api/parking_lot/${this.$route.params.id}`, {
                    method : "PUT",
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
    },
    mounted: async function() {
        const res = await fetch(`/api/parking_lot/${this.$route.params.id}`, {
            method: "GET",
            headers: {
                "Content-Type" : "application/json",
                "auth-token" : localStorage.getItem("auth_token")
            }
        })
        const data = await res.json()
        if (res.ok) {
            this.LotDetails.name = data.parking_lot_details.name
            this.LotDetails.address = data.parking_lot_details.address
            this.LotDetails.pincode = data.parking_lot_details.pincode
            this.LotDetails.no_of_spots = data.parking_lot_details.no_of_spots
            this.LotDetails.price = data.parking_lot_details.price
        }
    }
}