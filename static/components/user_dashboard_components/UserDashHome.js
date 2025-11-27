export default {
    template : `
        <div style="margin-bottom: 20px;">
            <div v-if="current_parkings.length != 0">
                <h2>Current Parkings</h2>
                <div style="border: 3px solid black; width: 900px; margin: 20px;">
                    <div v-for="parking in current_parkings" style="padding: 5px;">
                        <div style="border: 3px solid black;">
                            <div style="padding: 10px;">
                                <span style="font-size: xx-large;">{{parking.vehicle_reg_no}}</span>
                                <span style="margin-left: 25px; font-size: large;">Parking at <b>{{parking.lot_name}}</b> in {{parking.lot_address}}, <b>{{parking.lot_pincode}}</b></span>
                            </div>
                            <div style="margin: 0px 0px 10px 10px;">
                                <span style="font-size: large;"><b>Parking ID</b> : {{parking.id}}</span>
                                <span style="margin-left: 50px; font-size: large;"><b>Lot ID</b> : {{parking.lot_id}}</span>
                                <span style="margin-left: 50px; font-size: large;"><b>Spot No</b> : {{parking.spot_no}}</span>  
                            </div>
                            <div style="margin: 0px 0px 10px 10px;">
                                <span style="font-size: large;"><b>Parking Time</b> : {{parking.parking_time}}</span>
                                <span style="margin-left: 40px; font-size: large;"><b>Parking Rate</b> : Rs. {{parking.lot_price}}/hr</span>
                                <span style="float: right; padding-right: 50px;">
                                    <button @click="ReleaseParking(parking.id)" style="font-size: medium;">Release the Spot</button>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                <hr/>
            </div>
            <h2>Parking Lots</h2>  
            <p v-if="message != ''" style="color: red; margin-left: 20px;">{{message}}<p>
            <p v-if="parking_lots.length === 0" style="color: red; margin-left: 20px;">No parking lots available</p>
            <div v-else style="border: 3px solid black; width: 900px; border-radius: 3px; margin: 20px;">
                <p style="padding-left: 18px; font-size: large">Please enter your vehicle registration number : <input v-model="vehicle_reg_no" style="font-size: large; width: 150px" type=text placeholder="MH01BD5745"></p>
                <div v-for="lot in parking_lots" style="padding: 5px;">
                    <div style="border: 3px solid black; border-radius: 3px">
                        <div style="padding: 10px;">
                            <span style="font-size: xx-large;">{{lot.name}}</span>
                            <span style="padding-left: 15px; font-size: large;">{{lot.address}}, <b>{{lot.pincode}}</b></span>
                            <span style="float: right; padding-right: 20px; font-size: xx-large;">Rs. {{lot.price}}/hr</span>
                        </div>
                        <div  style="padding: 0px 0px 10px 10px;">
                            <span style="font-size: large;"><b>ID</b> : {{lot.id}}</span>
                            <span style="padding-left: 50px; font-size: large;"><b>Total Spots</b> : {{lot.no_of_spots}}</span>
                            <span style="padding-left: 50px; font-size: large;"><b>Spots Available</b> : {{lot.no_of_spots_available}}</span>
                            <span style="float: right; padding-right: 50px;">
                                <button @click="BookParking(lot.id)" style="font-size: medium;"> Book a Spot </button>
                            </span>
                        </div>
                    </div>
                </div>
            </div>   
        </div>    
    `,
    data: function() {
        return {
            parking_lots : [],
            current_parkings : [],
            vehicle_reg_no : "",
            message : ""       
        }
    },
    methods : {
        LoadData: async function() {
            const res = await fetch("/api/user", {
                method: "GET",
                headers: {
                    "auth-token" : localStorage.getItem("auth_token")
                }
            })    
            const data = await res.json()
            if (res.ok) {
                this.parking_lots = data.parking_lot_list,
                this.current_parkings = data.current_parkings
            }
        },
        BookParking: async function(id) {
            fetch(`/api/book_parking/${id}`, {
                method : "POST",
                headers: {
                    "auth-token" : localStorage.getItem("auth_token"),
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "vehicle_reg_no" : this.vehicle_reg_no 
                })
            }).then(res => res.json()).then(
                data => {
                    alert(data.message)
                    this.LoadData()
                }
            )
        },
        ReleaseParking: async function(id) {
            fetch(`/api/release_parking/${id}`, {
                method : "PUT",
                headers: {
                    "auth-token" : localStorage.getItem("auth_token"),
                }                
            }).then(res => res.json()).then(
                data => {
                    alert(data.message)
                    this.LoadData()
                }
            )
        }
    },
    mounted() {
        this.LoadData()
    }
}