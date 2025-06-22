// Global variables for person names
let person1Name = 'Person 1';
let person2Name = 'Person 2';

// Function to update UI with custom names
function updatePersonNamesUI() {
    // Update form labels
    $('label[for="person1_share"]').text(`${person1Name}'s Share (₹)`);
    $('label[for="person2_share"]').text(`${person2Name}'s Share (₹)`);
    
    // Update radio button labels
    $('label[for="paid_by_person1"]').text(person1Name);
    $('label[for="paid_by_person2"]').text(person2Name);
    
    // Update table headers
    $('th.person1-header').text(`${person1Name}'s Share (₹)`);
    $('th.person2-header').text(`${person2Name}'s Share (₹)`);
    
    // Update 'Paid By' column in the table
    $('.person1-name').text(person1Name);
    $('.person2-name').text(person2Name);
    
    // Update footer/summary section
    const summaryText = $('.card-body h4').text();
    if (summaryText.includes('Person 1') || summaryText.includes('Person 2')) {
        let newText = summaryText
            .replace(/Person 1/g, person1Name)
            .replace(/Person 2/g, person2Name);
        $('.card-body h4').text(newText);
    }
}

// Function to save names to localStorage
function saveNamesToStorage() {
    localStorage.setItem('person1Name', person1Name);
    localStorage.setItem('person2Name', person2Name);
}

// Function to load names from localStorage
function loadNamesFromStorage() {
    const savedPerson1 = localStorage.getItem('person1Name');
    const savedPerson2 = localStorage.getItem('person2Name');
    
    if (savedPerson1) person1Name = savedPerson1;
    if (savedPerson2) person2Name = savedPerson2;
    
    $('#person1Name').val(person1Name);
    $('#person2Name').val(person2Name);
    
    // Load collapse state from localStorage
    const collapseState = localStorage.getItem('nameCustomizationCollapsed');
    if (collapseState === 'true') {
        // Collapse is closed by default, no need to do anything
    } else if (collapseState === 'false') {
        // Open the collapse if it was previously open
        const collapseElement = document.getElementById('nameCustomizationCollapse');
        if (collapseElement) {
            new bootstrap.Collapse(collapseElement, { toggle: true });
        }
    }
    
    updatePersonNamesUI();
    
    // Initialize collapse state management
    const collapseElement = document.getElementById('nameCustomizationCollapse');
    if (collapseElement) {
        // Toggle arrow rotation on collapse
        collapseElement.addEventListener('show.bs.collapse', function() {
            const arrow = this.previousElementSibling.querySelector('.collapse-arrow');
            if (arrow) arrow.style.transform = 'rotate(180deg)';
            localStorage.setItem('nameCustomizationCollapsed', 'false');
        });
        
        collapseElement.addEventListener('hide.bs.collapse', function() {
            const arrow = this.previousElementSibling.querySelector('.collapse-arrow');
            if (arrow) arrow.style.transform = 'rotate(0deg)';
            localStorage.setItem('nameCustomizationCollapsed', 'true');
        });
    }
}

$(document).ready(function() {
    // Set today's date as default
    const today = new Date().toISOString().split('T')[0];
    $('#date').val(today);
    
    // Load saved names
    loadNamesFromStorage();
    
    // Handle name updates
    $('#updateNamesBtn').on('click', function() {
        const newPerson1 = $('#person1Name').val().trim() || 'Person 1';
        const newPerson2 = $('#person2Name').val().trim() || 'Person 2';
        
        person1Name = newPerson1;
        person2Name = newPerson2;
        
        saveNamesToStorage();
        updatePersonNamesUI();
        
        // Show success message
        const toast = new bootstrap.Toast(document.getElementById('toast'));
        document.getElementById('toastMessage').textContent = 'Names updated successfully';
        toast.show();
    });
    
    // Handle Enter key in name inputs
    $('#person1Name, #person2Name').on('keypress', function(e) {
        if (e.which === 13) { // Enter key
            e.preventDefault();
            $('#updateNamesBtn').click();
        }
    });
    
    // Initialize equal share functionality
    initEqualShare();
    
    // Auto-calculate shares when total amount changes
    $('#total_amount').on('input', function() {
        if ($('#equal_share').is(':checked')) {
            calculateEqualShares();
        }
    });
    
    // Handle save/update expense button click
    $('#saveExpense').on('click', function() {
        const expenseId = $(this).data('expense-id');
        if (expenseId) {
            updateExpense(expenseId);
        } else {
            saveExpense();
        }
    });
    
    // Handle paid_by radio button change
    $('input[name="paid_by"]').change(function() {
        calculateEqualShares();
    });
    
        // Handle manual share input
    $('#person1_share, #person2_share').on('input', function() {
        // If user manually enters a value, uncheck equal share
        if ($(this).val() !== '') {
            $('#equal_share').prop('checked', false);
            $('.share-input').prop('disabled', false);
        }
        updateRemainingAmount();
    });
    
    // Refresh button click handler removed - functionality no longer needed
    
    // Update remaining amount when amounts change
    $('#total_amount, #person1_share, #person2_share').on('input', function() {
        updateRemainingAmount();
    });
    
    // Initial remaining amount update
    updateRemainingAmount();
    
    // Handle edit expense button click
    $(document).on('click', '.edit-expense', function(e) {
        console.log('Edit button clicked');
        e.preventDefault();
        e.stopPropagation();
        const expenseId = $(this).data('id');
        console.log('Expense ID:', expenseId);
        const modal = $('#addExpenseModal');
        console.log('Modal found:', modal.length > 0);
        
        // Reset form
        $('#expenseForm')[0].reset();
        $('#expenseForm input').removeClass('is-invalid');
        $('#expenseId').val('');
        $('input[name="paid_by"]').prop('checked', false);
        $('#equal_share').prop('checked', true);
        $('.share-input').prop('disabled', true);
        updateRemainingAmount();
        
        // Update button text based on whether we're adding or editing
        const isEdit = expenseId !== '';
        $('#saveExpense').text(isEdit ? 'Update Expense' : 'Add Expense').data('expense-id', expenseId);
        
        // Fill form with expense data
        const row = $(this);
        const form = modal.find('form');
        const person1Share = parseFloat(row.data('person1_share'));
        const person2Share = parseFloat(row.data('person2_share'));
        const totalAmount = parseFloat(row.data('total_amount'));
        
        // Check if shares are equal to determine checkbox state
        const isEqualShare = (Math.abs((person1Share + person2Share) - totalAmount) < 0.01) && 
                           (Math.abs(person1Share - person2Share) < 0.01);
        
        // Set form values from data attributes
        form.find('#date').val(row.data('date'));
        form.find('#description').val(row.data('description'));
        form.find('#category').val(row.data('category'));
        form.find('#payment_mode').val(row.data('payment_mode'));
        form.find('#total_amount').val(totalAmount.toFixed(2));
        form.find(`input[name="paid_by"][value="${row.data('paid_by')}"]`).prop('checked', true);
        
        // Handle equal share checkbox and share inputs
        form.find('#equal_share').prop('checked', isEqualShare);
        form.find('#person1_share').val(person1Share.toFixed(2));
        form.find('#person2_share').val(person2Share.toFixed(2));
        form.find('.share-input').prop('disabled', isEqualShare);
        
        // Show the modal
        modal.modal('show');
    });
    
    // Handle delete expense button click
    $(document).on('click', '.delete-expense', function(e) {
        console.log('Delete button clicked');
        e.preventDefault();
        e.stopPropagation();
        const expenseId = $(this).data('id');
        console.log('Expense to delete ID:', expenseId);
        if (confirm('Are you sure you want to delete this expense? This action cannot be undone.')) {
            const expenseId = $(this).data('id');
            $.ajax({
                url: `/delete_expense/${expenseId}`,
                dataType: 'json',
                type: 'DELETE',
                success: function(response) {
                    if (response.success) {
                        window.location.reload();
                    } else {
                        alert('Error deleting expense: ' + (response.error || 'Unknown error'));
                    }
                },
                error: function() {
                    alert('Error connecting to server');
                }
            });
        }
    });
    
    // Reset modal when hidden
    $('#addExpenseModal').on('hidden.bs.modal', function () {
        const modal = $(this);
        modal.find('.modal-title').text('Add New Expense');
        modal.find('#saveExpense').text('Add Expense').removeData('expense-id');
        modal.find('form')[0].reset();
    });
});

function initEqualShare() {
    // Handle equal share checkbox change
    $('#equal_share').on('change', function() {
        const isChecked = $(this).is(':checked');
        
        // Enable/disable share inputs
        $('.share-input').prop('disabled', isChecked);
        
        // If enabling equal share, recalculate shares
        if (isChecked) {
            calculateEqualShares();
        }
    });
    
    // Initial calculation
    if ($('#equal_share').is(':checked')) {
        calculateEqualShares();
    }
}

function calculateEqualShares() {
    const totalAmount = parseFloat($('#total_amount').val()) || 0;
    const share = (totalAmount / 2).toFixed(2);
    
    // Update both share fields
    $('#person1_share').val(share);
    $('#person2_share').val(share);
    
    updateRemainingAmount();
}

function updateRemainingAmount() {
    const totalAmount = parseFloat($('#total_amount').val()) || 0;
    const person1Share = parseFloat($('#person1_share').val()) || 0;
    const person2Share = parseFloat($('#person2_share').val()) || 0;
    const remaining = totalAmount - (person1Share + person2Share);
    
    // Update the UI to show remaining amount
    const remainingElement = $('#remaining-amount');
    if (remainingElement.length === 0) {
        $('.modal-body').append(`
            <div class="alert alert-warning mt-3" id="remaining-amount">
                Remaining: ₹${remaining.toFixed(2)}
            </div>
        `);
    } else {
        remainingElement.text(`Remaining: ₹${remaining.toFixed(2)}`);
        remainingElement.toggleClass('alert-danger', Math.abs(remaining) > 0.01);
    }
}

function saveExpense() {
    const form = $('#expenseForm');
    
    // Create form data object
    const formData = {
        date: $('#date').val(),
        description: $('#description').val(),
        category: $('#category').val(),
        payment_mode: $('#payment_mode').val(),
        total_amount: parseFloat($('#total_amount').val() || 0),
        paid_by: $('input[name="paid_by"]:checked').val(),
        person1_share: parseFloat($('#person1_share').val() || 0),
        person2_share: parseFloat($('#person2_share').val() || 0)
    };
    
    console.log('Submitting form data:', formData);
    
    // Validate form
    let isValid = true;
    $('[required]').each(function() {
        if (!$(this).val()) {
            isValid = false;
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid');
        }
    });
    
    if (!isValid) {
        alert('Please fill in all required fields');
        return;
    }
    
    // Check if shares add up to total amount
    const totalAmount = formData.total_amount;
    const person1Share = formData.person1_share;
    const person2Share = formData.person2_share;
    const totalShares = person1Share + person2Share;
    const remaining = Math.abs(totalAmount - totalShares);
    
    if (remaining > 0.01) { // Allow for floating point precision
        if (!confirm(`The sum of shares (₹${totalShares.toFixed(2)}) does not equal the total amount (₹${totalAmount.toFixed(2)}). Do you want to continue anyway?`)) {
            return;
        }
    }
    
    // Submit the form as JSON
    $.ajax({
        type: 'POST',
        url: '/add_expense',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            console.log('Server response:', response);
            if (response.success) {
                window.location.reload();
            } else {
                alert('Error saving expense: ' + (response.error || 'Unknown error'));
            }
        },
        error: function(xhr, status, error) {
            console.error('Error saving expense:', status, error);
            console.error('Response text:', xhr.responseText);
            alert('Error connecting to server: ' + error);
        }
    });
}

function updateExpense(expenseId) {
    // Create form data object
    const formData = {
        date: $('#date').val(),
        description: $('#description').val(),
        category: $('#category').val(),
        payment_mode: $('#payment_mode').val(),
        total_amount: parseFloat($('#total_amount').val() || 0),
        paid_by: $('input[name="paid_by"]:checked').val(),
        person1_share: parseFloat($('#person1_share').val() || 0),
        person2_share: parseFloat($('#person2_share').val() || 0)
    };
    
    console.log('Updating expense with data:', formData);
    
    // Validate form
    let isValid = true;
    $('[required]').each(function() {
        if (!$(this).val()) {
            isValid = false;
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid');
        }
    });
    
    if (!isValid) {
        alert('Please fill in all required fields');
        return;
    }
    
    // Check if shares add up to total amount
    const totalAmount = formData.total_amount;
    const person1Share = formData.person1_share;
    const person2Share = formData.person2_share;
    const totalShares = person1Share + person2Share;
    const remaining = Math.abs(totalAmount - totalShares);
    
    if (remaining > 0.01) {
        if (!confirm(`The sum of shares (₹${totalShares.toFixed(2)}) does not equal the total amount (₹${totalAmount.toFixed(2)}). Do you want to continue anyway?`)) {
            return;
        }
    }
    
    // Submit the form as JSON
    $.ajax({
        type: 'PUT',
        url: `/edit_expense/${expenseId}`,
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            console.log('Server response:', response);
            if (response.success) {
                window.location.reload();
            } else {
                alert('Error updating expense: ' + (response.error || 'Unknown error'));
            }
        },
        error: function(xhr, status, error) {
            console.error('Error updating expense:', status, error);
            console.error('Response text:', xhr.responseText);
            alert('Error connecting to server: ' + error);
        }
    });
}
