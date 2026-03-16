# Persistent Storage - Complete Guide

> **Understanding Persistent Volumes, PVCs, and Storage Classes with real-world analogies**

This document explains persistent storage in Kubernetes and how it's used in the FreshHarvest Market project.

---

## 📚 Table of Contents

1. [What is Persistent Storage?](#what-is-persistent-storage)
2. [Why Do We Need It?](#why-do-we-need-it)
3. [Storage Concepts](#storage-concepts)
4. [How It Works](#how-it-works)
5. [Our Storage Configuration](#our-storage-configuration)
6. [Real-World Examples](#real-world-examples)

---

## 🎯 What is Persistent Storage?

### Real-World Analogy

Think of **Persistent Storage** as a **USB drive** vs **RAM**:

```
💻 Computer (Pod)
├── 🧠 RAM (Ephemeral Storage)
│   └── Data lost when computer shuts down ❌
│   └── Fast but temporary
│
└── 💾 USB Drive (Persistent Volume)
    └── Data survives restarts ✅
    └── Slower but permanent
```

### In Kubernetes

| Storage Type | Analogy | What Happens |
|--------------|---------|--------------|
| **Ephemeral** | RAM | Deleted when pod dies |
| **Persistent** | USB Drive | Survives pod restarts |
| **PVC** | Request for USB | "I need 20GB storage" |
| **PV** | Actual USB Drive | The storage itself |

---

## 🤔 Why Do We Need It?

### Problem: Data Loss

**Without Persistent Storage:**
```
1. Database pod starts
   ↓
2. User creates account (data stored)
   ↓
3. Pod crashes/restarts
   ↓
4. All data LOST! ❌
```

**With Persistent Storage:**
```
1. Database pod starts
   ↓
2. User creates account (data stored on PVC)
   ↓
3. Pod crashes/restarts
   ↓
4. New pod mounts same PVC
   ↓
5. Data still there! ✅
```

### Use Cases

- **Databases**: SQL Server, PostgreSQL, MySQL
- **File Storage**: Uploaded files, logs
- **Stateful Applications**: Message queues, caches

---

## 📦 Storage Concepts

### 1. PersistentVolume (PV)

A **PV** is a piece of storage in the cluster.

**Analogy:** A physical USB drive

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mssql-pv
spec:
  capacity:
    storage: 20Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: standard
```

### 2. PersistentVolumeClaim (PVC)

A **PVC** is a request for storage.

**Analogy:** "I need a 20GB USB drive"

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mssql-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

### 3. StorageClass

A **StorageClass** defines how storage is provisioned.

**Analogy:** Different types of USB drives (USB 2.0, USB 3.0, SSD)

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: kubernetes.io/hostpath
```

---

## 🔄 How It Works

### Step-by-Step Flow

```
1. You create a PVC
   ↓
2. Kubernetes finds/create a PV
   ↓
3. PVC binds to PV
   ↓
4. Pod mounts the PVC
   ↓
5. Data persists!
```

### Binding Process

```
PVC: "I need 20GB"
  ↓
Kubernetes: "Looking for available PV..."
  ↓
PV Found: "I have 20GB available"
  ↓
Binding: PVC ↔ PV
  ↓
Pod: "Mount this PVC"
  ↓
Data: Stored on PV ✅
```

---

## 🏗️ Our Storage Configuration

### Location

```
infra/k8s/
├── staging/storage/
│   ├── persistent-volume-claim.yaml
│   └── README.md
└── prod/storage/
    ├── persistent-volume-claim.yaml
    └── README.md
```

### Staging PVC

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mssql-data-pvc
  namespace: staging
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

**What it does:**
- Requests 20GB storage
- ReadWriteOnce (one pod at a time)
- For SQL Server database

### Production PVC

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mssql-data-pvc
  namespace: prod
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi  # Larger for production
```

---

## 💡 Real-World Examples

### Example 1: Create PVC

```bash
# Apply PVC
kubectl apply -f infra/k8s/staging/storage/

# Check status
kubectl get pvc -n staging

# Output:
# NAME            STATUS   VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
# mssql-data-pvc  Bound    pv-123   20Gi       RWO            standard       5s
```

### Example 2: Mount PVC to Pod

```yaml
# In deployment.yaml
spec:
  containers:
    - name: mssql
      volumeMounts:
        - name: mssql-data
          mountPath: /var/opt/mssql
  volumes:
    - name: mssql-data
      persistentVolumeClaim:
        claimName: mssql-data-pvc
```

### Example 3: Check Storage Usage

```bash
# Check PVC
kubectl get pvc mssql-data-pvc -n staging

# Describe PVC
kubectl describe pvc mssql-data-pvc -n staging

# Check PV
kubectl get pv
```

---

## 🔍 Access Modes

### ReadWriteOnce (RWO)

**Analogy:** USB drive (one computer at a time)

- Only one pod can mount
- Good for databases
- Most common

### ReadOnlyMany (ROX)

**Analogy:** CD-ROM (read-only, many computers)

- Multiple pods can read
- No writes allowed
- Good for shared configs

### ReadWriteMany (RWX)

**Analogy:** Network drive (many computers)

- Multiple pods can read/write
- Requires special storage (NFS, etc.)
- Good for shared files

---

## 🛠️ Storage Classes

### Docker Desktop (hostpath)

```yaml
storageClassName: hostpath
```

**What it does:** Uses local disk storage

### Cloud Providers

```yaml
# AWS EKS
storageClassName: gp2

# Azure AKS
storageClassName: managed-premium

# GCP GKE
storageClassName: standard
```

---

## 📊 Storage Lifecycle

### Provisioning

```
1. Create PVC
   ↓
2. StorageClass provisions PV
   ↓
3. PVC binds to PV
   ↓
4. Ready to use!
```

### Reclaiming

When PVC is deleted:

- **Retain**: PV kept (manual cleanup)
- **Delete**: PV deleted automatically
- **Recycle**: PV wiped and reused (deprecated)

---

## 🔗 How Storage Connects

### Complete Flow

```
User creates data
  ↓
Pod writes to /var/opt/mssql
  ↓
Data stored on PVC
  ↓
PVC backed by PV
  ↓
PV on physical storage
  ↓
Data persists! ✅
```

### In FreshHarvest Market

```
SQL Server Pod
├── Mounts: mssql-data-pvc
├── Path: /var/opt/mssql
├── Storage: 20Gi (staging) / 100Gi (prod)
└── Data: Survives pod restarts
```

---

## 📚 Related Documents

- **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** - How we implemented K8s
- **[ADVANCED_CONCEPTS.md](./ADVANCED_CONCEPTS.md)** - Advanced K8s concepts
- **[FILE_REFERENCE.md](./FILE_REFERENCE.md)** - Complete file reference

---

## 🎯 Key Takeaways

1. **Persistent Storage** = Data that survives pod restarts
2. **PVC** = Request for storage
3. **PV** = Actual storage resource
4. **StorageClass** = How storage is provisioned
5. **Use for**: Databases, file storage, stateful apps
6. **Access Modes**: RWO (one pod), RWX (many pods)

---

This completes the Storage guide! See other documents for more details. 🚀

---