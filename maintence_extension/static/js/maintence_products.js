odoo.define("maintence_extension.product_actions", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");

    publicWidget.registry.ProductActions = publicWidget.Widget.extend({
        selector: ".table.table-bordered",
        events: {
            'click .btn-primary': '_onEditProduct',
            'click .btn-danger': '_onDeleteProduct',
            'click .btn-success': '_onAddProduct',
        },

        _onEditProduct: function (e) {
            const productRow = $(e.currentTarget).closest('tr');
            const productId = productRow.data('product-id');
            const productQuantity = productRow.find('td').eq(1).text();

            this._rpc({
                route: '/my/maintenance_order/products',
                params: {},
            }).then(function (response) {
                const products = response.products;

                let productOptions = '';
                products.forEach(product => {
                    const selected = product.id == productId ? 'selected' : '';
                    productOptions += `<option value="${product.id}" ${selected}>${product.name}</option>`;
                });

                const editFormHtml = `
                    <div id="editProductModal" class="modal fade" tabindex="-1" role="dialog">
                        <div class="modal-dialog" role="document">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">Editar Producto</h5>
                                </div>
                                <div class="modal-body">
                                    <form id="editProductForm">
                                        <div class="form-group">
                                            <label for="productSelect">Producto</label>
                                            <select class="form-control" id="productSelect">
                                                ${productOptions}
                                            </select>
                                        </div>
                                        <div class="form-group">
                                            <label for="productQuantity">Cantidad</label>
                                            <input type="number" class="form-control" id="productQuantity" value="${productQuantity}">
                                        </div>
                                    </form>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                                    <button type="button" class="btn btn-primary" id="saveProductChanges">Guardar Cambios</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                $('body').append(editFormHtml);
                $('#editProductModal').modal('show');

                $('#saveProductChanges').on('click', function () {
                    const selectedProductId = $('#productSelect').val();
                    const updatedQuantity = $('#productQuantity').val();
                    const productId = productRow.data('product-id');

                    console.log("Selected Product Template ID:", selectedProductId);
                    console.log("Maintenance Request Product ID:", productId);

                    this._rpc({
                        route: '/my/maintenance_order/update_product',
                        params: {
                            id: productId,
                            product_template_id: selectedProductId,
                            quantity: updatedQuantity,
                        },
                    }).then(function (response) {
                        window.location.reload();
                    }).catch(function (error) {
                        console.error("Error updating product:", error);
                    });
                }.bind(this));
            }.bind(this));
        },

        _onDeleteProduct: function (e) {
            const productRow = $(e.currentTarget).closest('tr');
            const productId = productRow.data('product-id');

            this._rpc({
                route: '/my/maintenance_order/delete_product',
                params: {
                    id: productId,
                },
            }).then(function (response) {
                window.location.reload();
            }).catch(function (error) {
                console.error("Error deleting product:", error);
            });
        },

        _onAddProduct: function (e) {
            const maintenanceRequestId = $('#Addproductbtn').attr('maintence-id');
            console.log("Maintenance Request ID:", maintenanceRequestId);

            this._rpc({
                route: '/my/maintenance_order/products',
                params: {
                    maintenance_request_id: maintenanceRequestId,
                },
            }).then(function (response) {
                const products = response.products;
                let optionsHtml = '';
                products.forEach(function (product) {
                    optionsHtml += `<option value="${product.id}">${product.name}</option>`;
                });

                const addFormHtml = `
                    <div id="addProductModal" class="modal fade" tabindex="-1" role="dialog" data-maintenance-request-id="${maintenanceRequestId}">
                        <div class="modal-dialog" role="document">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">Añadir Producto</h5>
                                </div>
                                <div class="modal-body">
                                    <form id="addProductForm">
                                        <div class="form-group">
                                            <label for="existingProduct">Producto Existente</label>
                                            <select class="form-control" id="existingProduct">
                                                ${optionsHtml}
                                            </select>
                                        </div>
                                        <div class="form-group">
                                            <label for="newProductQuantity">Cantidad</label>
                                            <input type="number" class="form-control" id="newProductQuantity">
                                        </div>
                                    </form>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                                    <button type="button" class="btn btn-success" id="saveNewProduct">Guardar Producto</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                $('body').append(addFormHtml);
                $('#addProductModal').modal('show');

                $('#saveNewProduct').on('click', function () {
                    const selectedProductId = $('#existingProduct').val();
                    const newQuantity = $('#newProductQuantity').val();

                    this._rpc({
                        route: '/my/maintenance_order/add_product',
                        params: {
                            product_id: selectedProductId,
                            quantity: newQuantity,
                            maintenance_request_id: maintenanceRequestId,
                        },
                    }).then(function (response) {
                        window.location.reload();
                    }).catch(function (error) {
                        console.error("Error adding product:", error);
                    });
                }.bind(this));
            }.bind(this)).catch(function (error) {
                console.error("Error fetching products:", error);
            });
        }

    });
});