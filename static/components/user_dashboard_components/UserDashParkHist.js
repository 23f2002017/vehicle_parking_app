export default {
    template : `
        <div style="margin-bottom: 20px;">
            <h2>Past Parkings</h2>
            <p v-if="past_parkings.length === 0" style="color: red; margin-left: 20px;">No Parkings History Found</p>
            <div v-else style="border: 3px solid black; width: 900px; margin: 20px;">
                <div v-for="parking in past_parkings" style="padding: 5px;">
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
                            <span style="margin-left: 40px; font-size: large;"><b>Parking Rate</b> : ₹{{parking.lot_price}}/hr</span>
                        </div>
                        <div style="margin: 0px 0px 10px 10px;">
                            <span style="font-size: large;"><b>Exit Time</b> : {{parking.exit_time}}</span>
                            <span style="margin-left: 40px; font-size: large;"><b>Parking Cost</b> : ₹{{parking.cost}}</span>
                        </div>
                    </div>
                </div>
            </div> 
        </div>    
    `,
    data: function() {
        return {
            past_parkings : [],
            message : ""       
        }
    },
    mounted : function() {
        fetch("/api/parking_history", {
            method: "GET",
            headers: {
                "auth-token" : localStorage.getItem("auth_token")
            }
        })    
        .then(response => response.json())
        .then(data => this.past_parkings = data.parking_history)
    }
}