function data() {
    return {
        schedule: [],
        shippingDay: [],
        drivers: [],
        districts: [],
        shippingTypes: [],
        pendingShippings: [],

        offset: 0,
        selectedOrder: null,
        scheduleRange: '',
        
        auth: {
            email: '',
            password: '',
            user_id: null,
            level: null,
            name: '',
            role: '',
            image: '',
            default_image: 'static/images/users/default.jpg',
            token: null,
        },

        loginButton: {
            class: '',
            text: 'Iniciar Sesión',
        },

        page: {
            current: 'calendar'
        },

        pages: [
            { name: 'calendar', label: 'Calendario' },
            { name: 'history', label: 'Historial' },
            { name: 'clients', label: 'Clientes' },
            { name: 'workers', label: 'Colaboradores' }
        ],

        modal: {
            shipping: false,
            completed: false,
            transit: false,
            overlay: false,
        },

        process_shipping: {
            edit: '',
            button_text: 'Añadir',
            button_complete: 'Entregado',
            button_class: '',
            driver_id: null,
            document: '',
            document_id: null,
            name: '',
            email: '',
            phone: '',
            order_number: '',
            shipping_type_id: null,
            address: '',
            district_id: null,
            creation_date: '',
            disabled: false,
            send_email: 1,
            shipping_status_id: null,
        },
        socket: null,
        preview: null,
        imageFile: null,

        async processShipping(shipping_number){
            if (shipping_number){
                await this.getShipping(shipping_number);
            }

            if (this.process_shipping.shipping_status_id > 3){
                this.modal = {
                    completed: true,
                    overlay: true,
                };
            } else {
                this.modal = {
                    shipping: true,
                    overlay: true,
                };
            }
        },

        async onTheWay(){
            const payload = {
                purchase_order_number: this.process_shipping.order_number,
                shipping_status_id: 3,
                admin_id: this.auth.user_id
            };
            
            try {
                const response = await fetch('/api/order/set', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
        
                if (!response.ok) {
                    throw new Error('Error al asignar la orden.');
                }
                
                const data = {
                    phone: this.process_shipping.phone,
                    user: this.process_shipping.name
                };
                this.socket.emit("on_the_way", data);

                await this.updateSchedule();
                this.process_shipping.shipping_status_id = 3;
                //this.getSchedule();
                //this.getPendingShippings();
            } catch (error) {
                console.error('Error en la asignación:', error);
            }
        },
        
        async completeShipping() {
            if (!this.imageFile) {
                this.process_shipping.button_complete = 'Sube una foto';
                this.process_shipping.button_class = 'error';
                setTimeout(() => {
                    this.process_shipping.button_complete = 'Entregado';
                    this.process_shipping.button_class = '';
                }, 1500);
                return;
            }
        
            const maxWidth = 1024;
            const maxHeight = 1024;
        
            try {
                const resizedImage = await this.resizeImage(this.imageFile, maxWidth, maxHeight);
        
                const formData = new FormData();
                formData.append("image", resizedImage);
                formData.append("order_number", this.process_shipping.order_number);
        
                await this.uploadImage(formData);
                await this.updateOrderStatus(4);
        
                await this.updateSchedule();
                this.closeShipping();
        
            } catch (error) {
                console.error("Error en el proceso de entrega:", error);
            }
        },
        
        async rejectShipping() {
            await this.updateOrderStatus(6);
            await this.updateSchedule();
            this.closeShipping();
        },

        resizeImage(file, maxWidth, maxHeight) {
            return new Promise((resolve, reject) => {
                const img = new Image();
                const reader = new FileReader();
        
                reader.onload = (e) => {
                    img.onload = () => {
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
        
                        let width = img.width;
                        let height = img.height;
        
                        if (width > height) {
                            if (width > maxWidth) {
                                height *= maxWidth / width;
                                width = maxWidth;
                            }
                        } else {
                            if (height > maxHeight) {
                                width *= maxHeight / height;
                                height = maxHeight;
                            }
                        }
        
                        canvas.width = width;
                        canvas.height = height;
                        ctx.drawImage(img, 0, 0, width, height);
        
                        canvas.toBlob((blob) => {
                            if (blob) resolve(blob);
                            else reject(new Error("Error al redimensionar la imagen"));
                        }, file.type);
                    };
        
                    img.src = e.target.result;
                };
        
                reader.onerror = () => reject(new Error("Error al leer el archivo"));
                reader.readAsDataURL(file);
            });
        },
        
        async uploadImage(formData) {
            const response = await fetch('/api/photo/upload', {
                method: 'POST',
                body: formData
            });
        
            if (!response.ok) {
                throw new Error('Error al subir la imagen.');
            }
        },
        
        async updateOrderStatus(status) {
            const payload = {
                purchase_order_number: this.process_shipping.order_number,
                shipping_status_id: status,
                admin_id: this.auth.user_id
            };
        
            const response = await fetch('/api/order/set', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
        
            if (!response.ok) {
                throw new Error('Error al asignar la orden.');
            }
        },

        async updateSchedule(){
            this.socket.emit("update_schedule", {});
        },

        async showShipping(shipping_number){
            await this.getShipping(shipping_number);

            this.modal = {
                transit: true,
                overlay: true,
            };
        },

        closeShipping(){
            this.modal = {
                shipping: false,
                completed: false,
                overlay: false,
            };
  
            this.preview = null;
            this.imageFile = null;
            this.selectedOrder = null;

            this.process_shipping = {
                edit: '',
                button_text: 'Añadir',
                button_complete: 'Entregado',
                button_class: '',
                driver_id: this.selectFirstOption(this.drivers),
                document: '',
                document_id: null,
                name: '',
                email: '',
                phone: '',
                order_number: '',
                shipping_type_id: null,
                address: '',
                district_id: null,
                creation_date: '',
                disabled: false,
                send_email: 1,
                shipping_status_id: null,
            };
        },

        async checkImage(document) {
            const url = `static/images/users/${document}.jpg`;
            const response = await fetch(url, { method: 'GET' });
            this.auth.image = response.ok ? url : this.auth.default_image;
        },

        async login() {
            const payload = { email: this.auth.email, password: this.auth.password }
            try {
                const response = await fetch('/api/user/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
                
                const jsonData = await response.json();
                if (!response.ok) {
                    if (response.status === 400) {
                        this.loginButton.text = jsonData.data.message;
                        this.loginButton.class = 'error';
                        setTimeout(() => {
                            this.loginButton.text = 'Iniciar Sesión';
                            this.loginButton.class = '';
                        }, 1500);
                    }
                    return false;
                }
                const userData = jsonData.data;
                
                await this.checkImage(userData.document);
                this.auth.token = userData.token;
                this.auth.user_id = userData.user_id;
                this.auth.level = userData.level;
                this.auth.name = userData.name;
                this.auth.role = userData.role;

                //console.log(this.auth)
                localStorage.setItem('user_data', JSON.stringify(this.auth));
                await this.fetchData();

            } catch (e) {
                console.error('Error during login verification:', e.message);
            }
        },

        logout() {
            this.auth.token = null;
            this.auth.user_id = null;
            this.auth.level = null;
            this.auth.name = '';
            this.auth.role = '';
            this.auth.image = '';
            this.offset = 0;
            localStorage.removeItem('user_data'); 
        },

        async loginVerify() {
            const storedData = localStorage.getItem('user_data');

            if (storedData) {
                const userData = JSON.parse(storedData);
                this.auth.token = userData.token;
                this.auth.user_id = userData.user_id;
                this.auth.level = userData.level;
                this.auth.name = userData.name;
                this.auth.role = userData.role;
                this.auth.image = userData.image;

                const response = await fetch('/api/user/verify', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${userData.token}`,
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok) {
                    this.logout();
                    throw new Error('Sesión expirada');
                }   
                
            } else {
                throw new Error('No ha inicado sesión');
            }
            
        },
        async init() {
            try {
                this.socket = io("/");
 
                this.socket.on("update_schedule", (data) => {
                    console.log("Updating Schedule");
                    if (this.auth.level == 4) {
                        this.getPendingShippings();
                        this.getSchedule();
                    } else {
                        this.getShippingDay();
                    }
                });

                await this.loginVerify();
                await this.fetchData();

            } catch (error) {
                console.error('Error al iniciar la aplicación:', error.message);
            } 
        },

        async getShippingDay() {
            try {
                const response = await fetch(`/api/shipping/day?offset=${this.offset}`).then(res => res.json());
                this.shippingDay = response.data || { orders: [] }  ;
            } catch (error) {
                console.error('Error fetching schedule', error);
            }
        },
        
        async fetchData() {
            try {
                if (this.auth.level == 4) {
                    const [driversRes, districtsRes, shippingTypesRes] = await Promise.all([
                        fetch('/api/general/drivers').then(res => res.json()),
                        fetch('/api/general/districts').then(res => res.json()),
                        fetch('/api/general/shipping_types').then(res => res.json())
                    ]);

                    this.drivers = driversRes.data || [];
                    this.districts = districtsRes.data || [];
                    this.shippingTypes = shippingTypesRes.data || [];

                    this.process_shipping.driver_id = this.selectFirstOption(this.drivers);
                    this.getPendingShippings();
                    this.getSchedule();
                } else {
                    await this.getShippingDay();
                }
            } catch (error) {
                console.error('Error fetching data', error);
            }
        },
        
        selectFirstOption(options) {
            return options[0].id;
        },

        async getPendingShippings() {
            try {
                const response = await fetch('/api/order/pending').then(res => res.json());
                this.pendingShippings = response.data || [];
            } catch (error) {
                console.error('Error fetching schedule', error);
            }
        },

        async getShipping(shipping_id) {
            try {
                const response = await fetch(`/api/order/${shipping_id}`).then(res => res.json());
                const shipping = response.data || [];

                this.process_shipping = {
                    edit: shipping.number,
                    button_text: 'Actualizar',
                    button_complete: 'Entregado',
                    driver_id: shipping.driver_id,
                    document: shipping.client_document,
                    document_id: shipping.client_document_id,
                    name: shipping.client_name,
                    email: shipping.client_email,
                    phone: shipping.client_phone,
                    order_number: shipping.number,
                    shipping_type_id: shipping.shipping_type_id,
                    address: shipping.address,
                    district_id: shipping.district_id,
                    district_name: shipping.district_name,
                    creation_date: shipping.creation_date_format,
                    send_email: shipping.send_email,
                    shipping_status_id: shipping.shipping_status_id,
                    shipping_type_name: shipping.shipping_type_name,
                    proof: shipping.image_path,
                };

            } catch (error) {
                console.error('Error fetching schedule', error);
            }
        },

        async getSchedule() {
            try {
                const scheduleRes = await fetch(`/api/order/schedule?offset=${this.offset}`).then(res => res.json());
                this.schedule = scheduleRes.data || [];
                this.scheduleRange = this.getDateRange(this.schedule)
            } catch (error) {
                console.error('Error fetching schedule', error);
            }
        },

        getDateRange(data) {
            const dates = data.map(item => new Date(item.date));
            const startDate = dates[0];
            const endDate = dates[dates.length - 1];

            const getNames = (date) => {
                const months = [
                    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                ];
                return months[date.getMonth()];
            };

            const startMonth = getNames(startDate);
            const startYear = startDate.getFullYear();
            const endMonth = getNames(endDate);
            const endYear = endDate.getFullYear();

            if (startMonth === endMonth && startYear === endYear) {
                return `${startMonth} ${startYear}`;
            } else {
                return `${startMonth} ${startYear} - ${endMonth} ${endYear}`;
            }
        },

        today() {
            if (this.offset == 0) {
                return;
            }
            this.offset = 0;
            if (this.auth.level == 4) {
                this.getSchedule();
            } else {
                this.getShippingDay();
            }
        },

        next() {
            this.offset++;
            if (this.auth.level == 4) {
                this.getSchedule();
            } else {
                this.getShippingDay();
            }
        },

        prev() {
            this.offset--;
            if (this.auth.level == 4) {
                this.getSchedule();
            } else {
                this.getShippingDay();
            }
        },

        onDragStart(order) {
            this.selectedOrder = order;
        },

        isFutureOrToday(dateString) {
            if (!dateString) return false;
            const today = new Date();
            today.setHours(0, 0, 0, 0);
        
            const dateParts = dateString.split('-');
            const targetDate = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]);
        
            return targetDate >= today;
        },
        
        onDragOver(event, day=null) {
            event.preventDefault();
            if (day) {
                if (this.isFutureOrToday(day.date)) {
                    event.currentTarget.classList.add('drag-over');
                }
            }
        },
        
        onDragLeave(event) {
            event.currentTarget.classList.remove('drag-over');
        },
        
        async onDrop(day, schedule) {
            document.querySelectorAll('.order-container').forEach(container => {
                container.classList.remove('drag-over');
            });
        
            if (!this.selectedOrder) {
                console.error('No hay orden seleccionada.');
                return;
            }
        
            if (!this.isFutureOrToday(day.date)) {
                console.warn('No se puede soltar en fechas pasadas.');
                return;
            }
        
            if (this.selectedOrder.shipping_date == day.date && this.selectedOrder.schedule == schedule) {
                return;
            }
        
            const payload = {
                purchase_order_number: this.selectedOrder.number,
                shipping_date: day.date,
                shipping_status_id: 2,
                shipping_schedule_id: schedule,
                admin_id: this.auth.user_id
            };
        
            try {
                const response = await fetch('/api/order/set', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
        
                if (!response.ok) {
                    throw new Error('Error al asignar la orden.');
                }
                
                await this.updateSchedule();
                //this.getSchedule();
                //this.getPendingShippings();
            } catch (error) {
                console.error('Error en la asignación:', error);
            }
        },

        async onDropPending() {
            if (!this.selectedOrder) {
                console.error('No hay orden seleccionada.');
                return;
            }

            const payload = {
                purchase_order_number: this.selectedOrder.number,
                shipping_date: null,
                shipping_status_id: 1,
                shipping_schedule_id: null,
                admin_id: this.auth.user_id
            };

            try {
                const response = await fetch('/api/order/set', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error('Error al asignar la orden.');
                }

                //const data = await response.json();
                await this.updateSchedule();
                //this.getSchedule();
                //this.getPendingShippings();
            } catch (error) {
                console.error('Error en la asignación:', error);
            }
        },

        async fetchUserData(document) {
            if (!document) {
                console.error('Documento no proporcionado.');
                return;
            }
            try {
                if (this.process_shipping.disabled) {
                    this.process_shipping.document_id = '';
                    this.process_shipping.email = '';
                    this.process_shipping.name = '';
                    this.process_shipping.phone = '';
                }
                
                this.process_shipping.disabled = false;

                const response = await fetch(`/api/user/${document}`);
                if (!response.ok) {
                    console.log('Documeto no encontrado')
                    return;
                }
                const data = await response.json();
                if (data.success) {
                    this.process_shipping.document_id = data.data.id;
                    this.process_shipping.email = data.data.email;
                    this.process_shipping.name = data.data.name;
                    this.process_shipping.phone = data.data.phone;
                    this.process_shipping.disabled = true;
                } else {
                    console.warn('Respuesta de API no exitosa.');
                }
            } catch (error) {
                console.error('Error al obtener datos del usuario:', error);
            }
        },

        async saveOrder() {
            
            let email_overrite = [3, 4].includes(this.process_shipping.shipping_type_id) ? 0 : this.process_shipping.shipping_type_id;
            const payload = {
                purchase_order_number: this.process_shipping.order_number,
                shipping_type_id: email_overrite,
                driver_id: this.process_shipping.driver_id,
                admin_id: this.auth.user_id,
                address: this.process_shipping.address,
                district_id: this.process_shipping.district_id,
                creation_date: this.process_shipping.creation_date,
                send_email: this.process_shipping.send_email,
                comments: ""
            };

            if (this.process_shipping.document_id) {
                payload.client_id = this.process_shipping.document_id;
            } else {
                payload.client = {
                    document: this.process_shipping.document,
                    email: this.process_shipping.email,
                    name: this.process_shipping.name,
                    phone: this.process_shipping.phone,
                };
            }
            
            //console.log(payload)
            try {
                const response = await fetch('/api/order/add', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                }).then(res => res.json());


                if (!response.success) {
                    this.process_shipping.button_text = response.data.message;
                    this.process_shipping.button_class = 'error';
                    setTimeout(() => {
                        this.process_shipping.button_text = 'Añadir';
                        this.process_shipping.button_class = '';
                    }, 1500);

                    return;
                }
                
                //alert('Orden guardada exitosamente');
                //this.process_shipping.driver_id = this.selectFirstOption(this.drivers);
                await this.updateSchedule();
                //this.getPendingShippings();
                //this.getSchedule();
                this.closeShipping();
                
            } catch (error) {
                this.process_shipping.button_text = 'Error interno';
                this.process_shipping.button_class = 'error';
                setTimeout(() => {
                    this.process_shipping.button_text = 'Añadir';
                    this.process_shipping.button_class = '';
                }, 1500);
            }
        },
    };
}