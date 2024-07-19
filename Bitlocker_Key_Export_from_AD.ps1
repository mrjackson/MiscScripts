$Computers = Get-ADComputer -Filter *
foreach ($computer in $Computers) {
    $ComputerName = $computer.name
    write-host($ComputerName)

    # Get Computer Object
    $computerObject = Get-ADComputer -Filter {cn -eq $ComputerName } -Property msTPM-OwnerInformation, msTPM-TpmInformationForComputer

    # Check if the computer object has had a BitLocker Recovery Password backed up to AD
    $BitLockerObject = Get-ADObject -Filter {objectclass -eq 'msFVE-RecoveryInformation'} -SearchBase $computerObject.DistinguishedName -Properties 'msFVE-RecoveryPassword' | Select-Object -Last 1
    if($BitLockerObject.'msFVE-RecoveryPassword'){
        Write-Host($BitLockerObject)
        $BitLockerObject | Out-file -FilePath "$(get-date -f yyyy-MM-dd)_Bitlocker.txt" -Append
    }else{
        Write-Host("No Bitlocker Found")
    }

}